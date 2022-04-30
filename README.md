# Quick and dirty Sonos driver for Linux Pluseaudio.

Streaming standard pulseaudio audio sink stream to a sonos device.

Works and tested with IKEA SYMFONISK speakers on Ubuntu 20.04.

# Installation:

## Local
    pip3 install soco
    apt-get install alsa-utils ffmpeg pulseaudio-utils vlc
    wget -O sonos https://raw.githubusercontent.com/antonylesuisse/sonos/master/sonos.py
    chmod +x sonos

### Usage:

    usage: sonos.py [-h] [-d DEVICE] [-v VOLUME]

    optional arguments:
      -h, --help            show this help message and exit
      -d DEVICE, --device DEVICE
                            preferred Sonos device to play stream on
      -v VOLUME, --volume VOLUME


Type Ctrl-C to stop streaming to sonos.


## Docker

### Build the image

    docker build . -t sonos-stream:latest

### Usage

#### Docker run

    docker run --rm -it --net host -v ${XDG_RUNTIME_DIR}/pulse/native:/app/pulse.sock -e PULSE_SERVER=unix:/app/pulse.sock sonos_stream:latest

#### Docker Compose

    docker-compose up -d


# Multiple Sonos units

Currently this will only target a single Sonos device.  If you have more than one, you can specify a preferred device and it will attempt to control that one.  You can specify the IP address of the preferred device on the command line using `-d <IP>` or by setting the environment variable, `SONOS_DEVICE_IP=<IP>` within Docker.
