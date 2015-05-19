# -*- coding: utf-8 -*-
"""A simple MIDI monitor which prints incoming messages to an LCD."""

import pyb

from midi.midiin import MidiIn
from hd44780 import HD44780

BAUDRATE = 31250
POLL_INTERVAL = 1  # ms


class STM_LCDShield(HD44780):
    _default_pins = ('PD2','PD1','PD6','PD5','PD4','PD3')


class MidiMonitor:
    def __init__(self, lcd):
        self.lcd  = lcd

    def __call__(self, msg):
        s = " ".join("%02X " % b for b in msg) + "   " * (3 - len(msg))
        self.lcd.write(s, row=1)
        print(tuple(msg))


def main():
    serial = pyb.UART(2, BAUDRATE)
    lcd = STM_LCDShield()
    monitor = MidiMonitor(lcd)
    midiin = MidiIn(serial, monitor, debug=True)
    lcd.write("MIDI Mon ")
    pyb.delay(1000)
    lcd.write("ready")
    pyb.delay(1000)
    lcd.write("     ", col=9)

    while True:
        midiin.poll()
        pyb.delay(POLL_INTERVAL)


if __name__ == '__main__':
    main()
