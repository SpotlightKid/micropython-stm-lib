"""MicroPython module for handling push button with debouncing using timer."""

import micropython

try:
    from machine import Timer
    timer_init = lambda t, p, cb: t.init(period=p, callback=cb)
except ImportError:
    from pyb import Timer
    timer_init = lambda t, p, cb: t.init(freq=1000 // p, callback=cb)

# uncomment when debugging callback problems
#micropython.alloc_emergency_exception_buf(100)


class DebouncedSwitch:
    def __init__(self, sw, cb, arg=None, delay=50, tid=4):
        self.sw = sw
        # Create references to bound methods beforehand
        # http://docs.micropython.org/en/latest/pyboard/library/micropython.html#micropython.schedule
        self._sw_cb = self.sw_cb
        self._tim_cb = self.tim_cb
        self._set_cb = getattr(self.sw, 'callback', None) or self.sw.irq
        self.delay = delay
        self.tim = Timer(tid)
        self.callback(cb, arg)

    def sw_cb(self, pin=None):
        self._set_cb(None)
        timer_init(self.tim, self.delay, self._tim_cb)

    def tim_cb(self, tim):
        tim.deinit()
        if self.sw():
            micropython.schedule(self.cb, self.arg)
        self._set_cb(self._sw_cb if self.cb else None)

    def callback(self, cb, arg=None):
        self.tim.deinit()
        self.cb = cb
        self.arg = arg
        self._set_cb(self._sw_cb if cb else None)


def test_pyb(ledno=1):
    import pyb
    sw = pyb.Switch()
    led = pyb.LED(ledno)
    return DebouncedSwitch(sw, lambda l: l.toggle(), led)


def test_machine(swpin=4, ledpin=16):
    from machine import Pin
    sw = Pin(swpin, Pin.IN)
    led = Pin(ledpin, Pin.OUT)
    return DebouncedSwitch(sw, lambda l: l.value(not l.value()), led)
