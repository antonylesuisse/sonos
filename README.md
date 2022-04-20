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

    ./sonos

Type Ctrl-C to stop streaming to sonos.


## Docker

### Build the image

    docker build . -t sonos-stream:latest

### Usage

#### Docker run

    docker run --rm -it --net host -v ${XDG_RUNTIME_DIR}/pulse/native:/app/pulse.sock -e PULSE_SERVER=unix:/app/pulse.sock sonos_stream:latest

#### Docker Compose

    docker-compose up -d
