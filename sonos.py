#!/usr/bin/env python3
"""
Send audio from Pulse Audio to a Sonos device
    by Antony Lesuisse 2020, public domain
"""

import argparse
import socket
import subprocess
import sys
from io import BufferedReader
from queue import Empty, Queue
from threading import Thread
from typing import Any, List, Optional, Union

import soco  # type: ignore[import]

HTTP_PORT = 8888
STREAM_NAME = "linux_to_sonos.flac"


def get_ip() -> Any:
    """
    Return the main IP address of the system

    Returns:
        Any: IP address
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0)
    try:
        # doesn't even have to be reachable
        sock.connect(('10.255.255.255', 1))
        ip_addr = sock.getsockname()[0]
    except socket.gaierror:
        ip_addr = '127.0.0.1'
    finally:
        sock.close()
    return ip_addr


def run(cmd: str, shell: bool = False) -> str:
    """
    Function to run a command and return output

    Args:
        cmd (str): command to run
        shell (bool, optional): Whether the supplied command should utilise the shell.
            Defaults to False.

    Returns:
        str: _description_
    """
    command: Union[str, List[str]]
    if '|' in cmd:
        shell = True
        command = cmd
    else:
        command = cmd.split(' ')
    try:
        proc = subprocess.run(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        print(f'Command "{" ".join(error.cmd)}" failed: {error.stdout.decode("utf-8")}')
        return ''

    return proc.stdout.decode('utf-8').strip()


def sonos_discover(preferred: str = '') -> Optional[soco.core.SoCo]:
    """
    Discover a Sonos speaker

    Args:
        preferred (str, optional): IP of preferred Sonos device. Defaults to ''.

    Returns:
        Optional[soco.core.SoCo]: Sonos device found
    """
    for device in soco.discover():
        if not preferred:
            print(
                'No preferred Sonos device.  Returning the first one found: '
                f'{device.player_name}'
            )
            return device
        if preferred == device.ip_address:
            print(f'Preferred Sonos device found: {device.player_name}')
            return device

    return None


def sonos_play(sonos: soco.core.SoCo, volume: int) -> None:
    """
    Play content on the Sonos device

    Args:
        sonos (soco.core.SoCo): Sonos device
        volume (int): Volume level to set
    """
    sonos.clear_queue()
    sonos.add_uri_to_queue(f'http://{get_ip()}:{HTTP_PORT}/{STREAM_NAME}')
    sonos.play_from_queue(0)
    sonos.volume = volume
    sonos.play()


def get_all_audio_sinks() -> str:
    """
    Return the output from

    Returns:
        str: _description_
    """
    return run("pactl list sinks short | awk '{print $2}'")


def sonos_sink_exists() -> bool:
    """
    Check if the Sonos sink exists

    Returns:
        bool: True if found, False otherwise
    """
    return 'Sonos' in get_all_audio_sinks()


def pa_sink_load(volume: int) -> int:
    """
    Load the Pulse Audio sink for the Sonos

    Args:
        volume (int): Initial volume to set

    Returns:
        int: ID of PA module just loaded.  Defaults to 0 if no module was loaded
    """
    module_id = 0
    sonos_sink = sonos_sink_exists()
    if not sonos_sink:
        print('Loading PA module')
        module_id = int(
            run(
                'pactl load-module module-combine-sink sink_name=Sonos '
                'sink_properties=device.description=Sonos slaves=@DEFAULT_SINK@ channels=2'
            )
        )
        sonos_sink = sonos_sink_exists()

    if sonos_sink:
        run('pactl set-sink-mute @DEFAULT_SINK@ true')
        run(f'pactl set-sink-volume Sonos {volume}%')
        run('pactl set-default-sink Sonos')

    return module_id


def pa_sink_unload(module_id: int) -> None:
    """
    Unload the Pule Audio sink for the Sonos

    Args:
        module_loaded (bool): Set true if we should attempt to unload the PA module
        original_sink (str, optional): Reset the default sink back to this value. Defaults to ''.
    """
    if module_id:
        print('Unloading PA module')
        run(f'pactl unload-module {module_id}')
        run('pactl set-sink-mute @DEFAULT_SINK@ false')


def vlc() -> subprocess.Popen:  # type: ignore[type-arg]
    """
    Use VLC to transcode and send the audio as a FLAC stream

    Returns:
        subprocess.Popen: process handle for VLC
    """
    command = (
        "/usr/bin/cvlc "
        "pulse://Sonos.monitor "
        "--sout #transcode{vcodec=none,acodec=flac,"
        "ab=1441,channels=2,samplerate=44100,scodec=none}:standard"
        f"{{access=http,dst=/{STREAM_NAME}}} "
        f'--http-host={get_ip()} '
        f'--http-port={HTTP_PORT}'
    )
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        command.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc


def silence() -> subprocess.Popen:  # type: ignore[type-arg]
    """
    Play a very quiet Pink noise to avoid sonos to cut when there is silence

    Returns:
        subprocess.Popen: process handle for ffplay
    """
    command = "ffplay -loglevel 24 -nodisp -autoexit -f lavfi -i anoisesrc=c=pink:r=44100:a=0.001"
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        command.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc


def stream_queue(stream: BufferedReader, queue: Queue) -> None:  # type: ignore[type-arg]
    """
    Read from a stream and push it to a queue

    Args:
        stream (BufferedReader): stream to follow
        queue (Queue): queue to write to
    """
    while not stream.closed:
        for line in iter(stream.readline, b''):
            queue.put(line)
    stream.close()


if __name__ == '__main__':

    def parse_args() -> argparse.Namespace:
        """
        Parse the command line arguments

        Returns:
            argparse.Namespace: parsed arguments
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '-d',
            '--device',
            help='preferred Sonos device to play stream on',
        )

        parser.add_argument(
            '-v',
            '--volume',
            default=60,
            type=int,
        )

        return parser.parse_args()

    def main() -> int:
        """
        Main program
        """
        args = parse_args()

        module_id = pa_sink_load(args.volume)

        if not sonos_sink_exists():
            print('No Sonos audio sink exists.')
            return 5

        silence_proc = silence()

        sonos = sonos_discover(preferred=args.device)
        if not sonos:
            print('No Sonos devices found')
            return 3

        vlc_proc = vlc()
        if not vlc_proc.stdout:  # or not vlc_proc.stderr:
            print('There was a problem with VLC.  Check errors.')
            return 4

        # Set up a thread and queue to read from the VLC CLI output
        queue = Queue()  # type: ignore[var-annotated]
        thread = Thread(target=stream_queue, args=(vlc_proc.stdout, queue))
        thread.daemon = True
        thread.start()

        sonos_play(sonos, args.volume)

        try:
            while True:
                try:
                    buffer = queue.get_nowait().decode().strip()
                except Empty:
                    if vlc_proc.stdout.closed:
                        print('Waiting for background thread to exit')
                        thread.join()
                        raise EOFError from Empty
                    continue
                print(buffer)
        except (EOFError, KeyboardInterrupt):
            print('Killing ffplay')
            silence_proc.terminate()
            print('Killing VLC')
            vlc_proc.terminate()
            pa_sink_unload(module_id)

        return 0

    sys.exit(main())
