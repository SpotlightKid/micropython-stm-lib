# -*- coding: utf-8 -*-
"""MicroPython rotary encoder library."""

import pyb


ENC_STATES = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)


class Encoder(object):
    def __init__(self, pin_x, pin_y, pin_mode=pyb.Pin.PULL_NONE, scale=1,
                 min=0, max=100, reverse=False):
        self.pin_x = (pin_x if isinstance(pin_x, pyb.Pin) else
                      pyb.Pin(pin_x, pyb.Pin.IN, pin_mode))
        self.pin_y = (pin_y if isinstance(pin_y, pyb.Pin) else
                      pyb.Pin(pin_y, pyb.Pin.IN, pin_mode))

        self.pin_mode = pin_mode
        self.scale = scale
        self.min = min
        self.max = max
        self.reverse = 1 if reverse else -1

        # The following variables are assigned to in the interrupt callback,
        # so we have to allocate them here.
        self._pos = -1
        self._readings = 0
        self._state = 0

        self.set_callbacks(self._callback)

    def _callback(self, line):
        self._readings = (self._readings << 2 | self.pin_x.value() << 1 |
                          self.pin_y.value()) & 0x0f

        self._state = ENC_STATES[self._readings] * self.reverse

        if self._state:
            self._pos = min(max(self.min, self._pos + self._state), self.max)

    def set_callbacks(self, callback=None):
        self.irq_x = pyb.ExtInt(self.pin_x, pyb.ExtInt.IRQ_RISING_FALLING,
                                self.pin_mode, callback)
        self.irq_y = pyb.ExtInt(self.pin_y, pyb.ExtInt.IRQ_RISING_FALLING,
                                self.pin_mode, callback)

    @property
    def position(self):
        return self._pos * self.scale

    def reset(self):
        self._pos = 0
