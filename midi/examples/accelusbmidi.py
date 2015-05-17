# -*- coding: utf-8 -*-
"""Demonstration of using the MIDI library with the USB-Serial interface.

To use this, connect the Discovery board to the computer with a USB cable
to the micro USB OTG connector and start a serial-to-MIDI converter program
on the host computer::

    ttymidi -s /dev/ttyACM0 [-v]

And then use aconnect, qjackctl or similar to connect the ttymidi port to
the input of your MIDI client.

"""

from midi.midiout import MidiOut


def main():
    import pyb

    serial = pyb.USB_VCP()
    midi = MidiOut(serial, channel=1)
    switch = pyb.Switch()

    if hasattr(pyb, 'Accel'):
        accel = pyb.Accel()
        SCALE = 1.27
    else:
        from staccel import STAccel
        accel = STAccel()
        SCALE = 127

    while True:
        while not switch():
            pyb.delay(10)

        note = abs(int(accel.x() * SCALE))
        velocity = abs(int(accel.y() * SCALE))
        midi.note_on(note, velocity)

        while switch():
            pyb.delay(50)

        midi.note_off(note)


if __name__ == '__main__':
    main()
