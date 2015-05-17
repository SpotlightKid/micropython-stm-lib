# -*- coding: utf-8 -*-
"""Demonstration of using the HD44780 library with the DFRobot LCDShield.

To use this, connect the Discovery board to the LCDSHield like this::

    Pin  LCDShield  STM32F4Dicovery
    ---  ---------  ---------------
    D4   D4         PD6
    D5   D5         PD5
    D6   D6         PD4
    D7   D7         PD3
    RS   D8         PD2
    EN   D9         PD1
    VDD  5V         5V
    VSS  GND        GND

"""

import pyb

from hd44780 import HD44780


class STM_LCDShield(HD44780):
    _default_pins = ('PD2','PD1','PD6','PD5','PD4','PD3')


def main():
    lcd = STM_LCDShield()

    lcd.write("ABCDEFGHIJKLMNOP")         # Send a string
    lcd.write("1234567890123456", row=1)  # Second line

    pyb.delay(3000) # 3 second delay
    lcd.clear()
    pyb.delay(500)

    # Send some more
    lcd.write("Hello, PyCologne")
    lcd.write("from MicroPython", row=1)


if __name__ == '__main__':
    main()
