# -*- coding: utf-8 -*-
"""MicroPython rotary encoder library.

Usage:

    from time import sleep_ms
    from encoder import Encoder

    # Connect CLK to D6, DT to D5, GND to GND and + to 3V3
    enc = Encoder(pin_clk=12, pin_dt=14, clicks=4)
    enc.on_change(print)

    while True:
        sleep_ms(50)

"""

from machine import Pin

ENC_STATES = (
    0,   # 00 00
    -1,  # 00 01
    1,   # 00 10
    0,   # 00 11
    1,   # 01 00
    0,   # 01 01
    0,   # 01 10
    -1,  # 01 11
    -1,  # 10 00
    0,   # 10 01
    0,   # 10 10
    1,   # 10 11
    0,   # 11 00
    1,   # 11 01
    -1,  # 11 10
    0    # 11 11
)
ACCEL_THRESHOLD = const(5)


class Encoder(object):
    def __init__(self, pin_clk, pin_dt, pin_mode=None, clicks=1, init_val=0,
                 min_val=0, max_val=100, accel=0, reverse=False, flag=None):
        self.pin_clk = (pin_clk if isinstance(pin_clk, Pin) else
                        Pin(pin_clk, Pin.IN, pin_mode))
        self.pin_dt = (pin_dt if isinstance(pin_dt, Pin) else
                       Pin(pin_dt, Pin.IN, pin_mode))

        self.min_val = min_val * clicks
        self.max_val = max_val * clicks
        self.accel = int((max_val - min_val) / 100 * accel)
        self.max_accel = int((max_val - min_val) / 2)
        self.clicks = clicks
        self.reverse = 1 if reverse else -1
        self._flag = flag

        # The following variables are assigned to in the interrupt callback,
        # so we have to allocate them here.
        self.value = init_val
        self._raw_value = init_val * clicks
        self._readings = 0
        self._state = 0
        self.cur_accel = 0

        self.set_isr(self._isr)

    def _isr(self, line):
        self._readings = (self._readings << 2 | self.pin_clk.value() << 1 |
                          self.pin_dt.value()) & 0x0f

        self._state = ENC_STATES[self._readings] * self.reverse

        if self._state:
            self.cur_accel = min(self.max_accel, self.cur_accel + self.accel)

            self._raw_value = min(self.max_val, max(self.min_val, self._raw_value +
                                  (1 + (self.cur_accel >> ACCEL_THRESHOLD)) *
                                  self._state))

            if self._flag is not None:
                self._flag.set()

    def poll(self, cb=None):
        self.cur_accel = max(0, self.cur_accel - self.accel)
        new_value = self._raw_value // self.clicks

        if new_value != self.value:
            self.value = new_value

            if cb:
               cb(self.value)

            return new_value

    def set_isr(self, callback=None):
        mode = Pin.IRQ_RISING | Pin.IRQ_FALLING
        self.irq_clk = self.pin_clk.irq(trigger=mode, handler=callback)
        self.irq_dt = self.pin_dt.irq(trigger=mode, handler=callback)

    def close(self):
        self.set_isr(None)
        self.irq_clk = self.irq_dt = None

    def reset(self, value=0):
        self._raw_value = value * self.clicks


def test(enc=None, **kwargs):
    from time import sleep_ms
    rate = kwargs.pop('rate', 20)

    if not isinstance(enc, Encoder):
        cls = kwargs.pop('encoder_cls', Encoder)
        kwargs.setdefault('pin_clk', 12)
        kwargs.setdefault('pin_dt', 14)
        kwargs.setdefault('clicks', 4)
        enc = cls(**kwargs)

    oldval = 0
    try:
        while True:
            val = enc.value
            if oldval != val:
                print(val)
                oldval = val

            enc.cur_accel = max(0, enc.cur_accel - enc.accel)
            sleep_ms(1000 // rate)
    except:
        enc.close()
