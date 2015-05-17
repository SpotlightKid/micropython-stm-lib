# -*- coding: utf-8 -*-
"""Read encoder and print position value to LCD."""

import pyb

from encoder import Encoder
from hd44780 import HD44780


class STM_LCDShield(HD44780):
    _default_pins = ('PD2','PD1','PD6','PD5','PD4','PD3')


def main():
    lcd.set_string("Value: ")
    lastpos = e.position

    while True:
        if lastpos != e.position:
            lastpos = e.position
            lcd.set_cursor(6, 0)
            for c in "%3i" % lastpos:
                lcd.send_byte(c)
        pyb.delay(100)


if __name__ == '__main__':
    lcd = STM_LCDShield()
    e = Encoder('A0', 'A1', pyb.Pin.PULL_UP, max=400, scale=0.25)
    main()
