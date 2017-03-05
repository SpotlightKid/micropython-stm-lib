# -*- coding: utf-8 -*-
"""MicroPython rotary encoder library for Pyboard/STMHal.

Usage:

    from time import sleep_ms
    from pyb_encoder import Encoder

    enc = Encoder(pin_clk='X11', pin_dt='X12')

    def readloop(enc):
        oldval = 0
        while True:
            val = enc.value
            if oldval != val:
                print(val)
                oldval = val
            sleep_ms(50)

    readloop(enc)
"""

from machine import Pin
from pyb import ExtInt
from encoder import Encoder as BaseEncoder, test as _test


class Encoder(BaseEncoder):
    def __init__(self, *args, **kwargs):
        self.pin_mode = kwargs.setdefault('pin_mode', Pin.PULL_NONE)
        super().__init__(*args, **kwargs)

    def set_callbacks(self, callback=None):
        mode = ExtInt.IRQ_RISING_FALLING
        self.irq_clk = ExtInt(self.pin_clk, mode, self.pin_mode, callback)
        self.irq_dt = ExtInt(self.pin_dt, mode, self.pin_mode, callback)


def test(enc=None, **kwargs):
    if not enc:
        kwargs.setdefault('pin_clk', 'X11')
        kwargs.setdefault('pin_dt', 'X12')
        kwargs.setdefault('encoder_cls', Encoder)
    _test(enc, **kwargs)
