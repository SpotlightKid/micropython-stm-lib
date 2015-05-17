# -*- coding: utf-8 -*-
"""Unit tests for MicroPython MIDI library."""

import sys
sys.path.insert(0, '..')

from midi.midiout import MidiOut


class MockUART:
    def __init__(self, *args, **kw):
        self.buf = bytearray()

    def write(self, buf):
        self.buf.extend(buf)
        return len(buf)

def setup():
    global midi, serial

    serial = MockUART()
    midi = MidiOut(serial)

def teardown():
    global midi, serial
    del midi, serial

def test_note_on():
    midi.note_on(60)
    assert serial.buf == b'\x90<\x7f'

def test_note_off():
    midi.note_off(60)
    assert serial.buf == b'\x80<\0'


if __name__ == '__main__':
    lcls = locals().copy()
    setup = lcls.get('setup')
    teardown = lcls.get('teardown')

    for name, obj in lcls.items():
        if callable(setup):
            setup()

        if name.startswith('test_') and callable(obj):
            print("%s ... " % name, end="")
            try:
                    obj()
            except AssertionError as exc:
                print("FAILED")
                print(exc)
            else:
                print("OK")

        if callable(teardown):
            teardown()
