# -*- coding: utf-8 -*-

import pyb

from encoder import Encoder


def main():
    e = Encoder('A0', 'A1', pyb.Pin.PULL_UP)
    lastpos = e.position

    while True:
        if lastpos != e.position:
            lastpos = e.position
            print(lastpos)
        pyb.delay(100)


if __name__ == '__main__':
    main()
