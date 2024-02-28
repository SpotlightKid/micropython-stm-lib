"""Convenience wrapper class for a single WS2812B RGB LED based on NeoPixel."""

from machine import Pin
from neopixel import NeoPixel


def parse_hexcolor(s):
    if s.startswith("#"):
        c = s[1:]
        if len(c) == 3:
            return tuple(int(ch + ch, 16) for ch in c)
        elif len(c) == 6:
            # MicroPython doesn't support slicing with step > 1
            return tuple(int(c[i:i+2], 16) for i in range(0, len(c), 2))

    raise Value(f"Invalid hex color string: {s}")


class RGBLED:
    def __init__(self, pin, idx=0, colormode="GRB", timing=1):
        self._idx = idx
        self._cm = colormode
        self._pin = Pin(pin, Pin.OUT)
        self._np = NeoPixel(self._pin, 1, timing=timing)
        self._rgb = (0, 0, 0)

    def __call__(self, r=None, g=None, b=None, brightness=1.0, write=True):
        if isinstance(r, str):
            r, g, b = parse_hexcolor(r)
        elif r is None and g is None and b is None:
            return self._rgb

        if r is None:
            r = self._rgb[0]
        if g is None:
            g = self._rgb[1]
        if b is None:
            b = self._rgb[2]

        self._rgb = (r, g, b)
        self.brightness(brightness, write=write)

    def _set(self, r, g, b, write=True):
        if self._cm == "GRB":
            r, g = g, r

        self._np[self._idx] = (r, g, b)

        if write:
            self._np.write()

    def brightness(self, val=1.0, write=True):
        r, g, b = (min(255, int(c * val)) for c in self._rgb)
        self._set(r, g, b, write=write)

