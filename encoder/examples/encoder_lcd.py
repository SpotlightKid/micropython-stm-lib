"""Read encoder and show position value on HD44780 LCD."""

from time import sleep_ms
from pyb_encoder import Encoder
from hd44780 import HD44780


class STM_LCDShield(HD44780):
    _default_pins = ('PD2', 'PD1', 'PD6', 'PD5', 'PD4', 'PD3')


def main():
    lcd.set_string("Value: ")

    while True:
        if (val := enc.poll()) is not None:
            lcd.set_cursor(6, 0)
            for c in "%3i" % val:
                lcd.send_byte(c)

        sleep_ms(50)


if __name__ == '__main__':
    lcd = STM_LCDShield()
    enc = Encoder('A0', 'A1', max_val=999, accel=5)
    main()
