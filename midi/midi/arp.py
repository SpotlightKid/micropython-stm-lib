# -*- coding: utf-8 -*-
"""MicroPython MIDI arpeggiator.

FIXME: not implemented yet

"""

from .constants import *


class Arp:
    """MIDI arpeggiator class."""

    def __init__(self, tempo=120, rate="1/8", range=1, , direction="up",
                 order="as played", channel=None, debug=False):
        self.tempo = tempo
        self.rate = rate
        self.gate = gate
        self.range = range
        self.direction = direction
        self.order = order
        self.debug = debug

    def __repr__(self):
        return '<Arp: channel={}>'.format(self.channel)

    def add(self, notes):
        """Add notes to the note buffer."""
        pass

    def remove(self, notes):
        """Remove notes from the note buffer."""
        pass

    def update(self, millis):
        """Update arpeggiator state advancing time."""
        pass
