# -*- coding: utf-8 -*-

from machine import sleep_ms
from pyb_encoder import Encoder


def main():
    enc = Encoder('A0', 'A1')
    lastval = 0

    while True:
        val = enc.value
        if lastval != val:
            lastval = val
            print(val)
        sleep_ms(50)


if __name__ == '__main__':
    main()
