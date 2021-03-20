# Quick and dirty Sonos driver for Linux Pluseaudio.

Streaming standard pulseaudio audio sink stream to a sonos device.

Works and tested with IKEA SYMFONISK speakers on Ubuntu 20.04.

## Requirements:

    pip3 install soco
    apt-get install alsa-utils ffmpeg pulseaudio-utils vlc

## Installation:

    wget -O sonos  https://raw.githubusercontent.com/antonylesuisse/sonos/master/sonos
    chmod +x sonos

## Usage:

    ./sonos

Type Ctrl-C to stop streaming to sonos.

Volume synchro from pulseaudio to the device is very hackish it always reset to
the master pulse audio to 75% after transmiting the delta volume change.

## Soco 0.11.1 device detection fix

I have been using and old soco version 0.11.1 and I had to apply the following
patch to fix the device detection. The patched core.py file is also available
in this repo. This might not be necessary anymore with newer versions.

    --- core_orig.py	2015-06-11 17:44:34.000000000 +0200
    +++ core.py	2021-03-20 19:02:15.679004126 +0100
    @@ -761,7 +761,8 @@
             self._all_zones.clear()
             self._visible_zones.clear()
             # Loop over each ZoneGroup Element
    -        for group_element in tree.findall('ZoneGroup'):
    +        for group_element in tree.find('ZoneGroups').findall('ZoneGroup'):
                 coordinator_uid = group_element.attrib['Coordinator']
                 group_uid = group_element.attrib['ID']
                 group_coordinator = None


