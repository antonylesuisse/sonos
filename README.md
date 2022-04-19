# Quick and dirty Sonos driver for Linux Pluseaudio.

Streaming standard pulseaudio audio sink stream to a sonos device.

Works and tested with IKEA SYMFONISK speakers on Ubuntu 20.04.

## Requirements:

    pip3 install -r requirements.txt
    apt-get install alsa-utils ffmpeg pulseaudio-utils vlc

## Installation:

    wget -O sonos  https://raw.githubusercontent.com/antonylesuisse/sonos/master/sonos.py
    chmod +x sonos

## Usage:

    ./sonos

Type Ctrl-C to stop streaming to sonos.
