# -*- coding: utf-8 -*-
"""Unit tests for MicroPython MIDI library."""

import sys
sys.path.insert(0, '..')

from midi.midiin import MidiIn
from midi.constants import NOTE_ON, NOTE_OFF


class MockUART:
    def __init__(self, data):
        self.buf = list(data)

    def read(self, *args):
        return bytes([self.buf.pop(0)])

    def any(self):
        return bool(self.buf)

class StdOutCapture:
    def __init__(self):
        self.buf = []
        self.pos = 0
    def write(self, s):
        self.buf.extend(s)


def cb(msg):
    msg = tuple(msg)
    #print("Msg: %r " % (msg,))
    messages.append(msg)


def setup():
    global midi, serial, messages

    messages = []


def test_channel_voice():
    """Test channel voice messages."""
    serial = MockUART([0x91, 60, 127, 0xD1, 20, 0xD1, 40, 0x81, 60, 64])
    midi = MidiIn(serial, cb, debug=True)
    midi.poll()
    assert len(messages) == 4
    assert messages[0] == (0x91, 60, 127)
    assert messages[1] == (0xD1, 20)
    assert messages[2] == (0xD1, 40)
    assert messages[3] == (0x81, 60, 64)


def test_running_status():
    """Test running status."""
    serial = MockUART([0x91, 60, 127, 0xD1, 20, 0xF8, 40, 60, 0x81, 60, 64])
    midi = MidiIn(serial, cb, debug=True)
    midi.poll()
    assert len(messages) == 6
    assert messages[0] == (0x91, 60, 127)
    assert messages[1] == (0xD1, 20)
    assert messages[2] == (0xF8,)
    assert messages[3] == (0xD1, 40)
    assert messages[4] == (0xD1, 60)
    assert messages[5] == (0x81, 60, 64)


if __name__ == '__main__':
    lcls = locals().copy()
    setup = lcls.get('setup')
    teardown = lcls.get('teardown')

    for name, obj in lcls.items():
        if callable(setup):
            setup()

        if name.startswith('test_') and callable(obj):
            docstring = getattr(obj, '__doc__', None)
            if docstring:
                print(docstring.splitlines()[0].strip(), end=" ... ")
            else:
                print(name, end=" ... ")

            try:
                #oldstdout = sys.stdout
                #sys.stdout = StdOutCapture()
                obj()
            except AssertionError as exc:
                #sys.stdout = oldstdout
                print("FAILED")
                print(exc)
            else:
                #sys.stdout = oldstdout
                print("OK")

        if callable(teardown):
            teardown()
