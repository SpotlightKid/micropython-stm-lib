# -*- coding: utf-8 -*-
"""Read encoder and print position value to LCD."""

from machine import sleep_ms
from pyb_encoder import Encoder
from hd44780 import HD44780


class STM_LCDShield(HD44780):
    _default_pins = ('PD2', 'PD1', 'PD6', 'PD5', 'PD4', 'PD3')


def main():
    lcd.set_string("Value: ")
    lastval = 0

    while True:
        val = enc.value
        if lastval != val:
            lastval = val
            lcd.set_cursor(6, 0)
            for c in "%3i" % val:
                lcd.send_byte(c)

        enc.cur_accel = max(0, enc.cur_accel - enc.accel)
        sleep_ms(50)


if __name__ == '__main__':
    lcd = STM_LCDShield()
    enc = Encoder('A0', 'A1', max_value=999, accel=5)
    main()
