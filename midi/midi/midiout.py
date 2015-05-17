# -*- coding: utf-8 -*-
"""MicroPython MIDI output library."""

from .constants import *


class MidiOut:
    """MIDI output class."""

    def __init__(self, device, channel=1):
        if not hasattr(device, 'write'):
            raise TypeError("device instance must have a 'write' method.")

        if channel < 1 or channel > 16:
            raise ValueError('channel must be an integer between 1..16.')

        self.device = device
        self.channel = channel

    def __repr__(self):
        return '<MidiOut: device={} channel={}>'.format(
            self.device, self.channel)

    def send(self, msg):
        """Send a MIDI message to the serial device."""
        return self.device.write(bytearray(msg))

    # Channel Mode Messages

    def channel_message(self, command, *data, ch=None):
        """Send a MIDI channel mode message to the serial device."""
        command = (command & 0xF0) | ((ch if ch else self.channel) - 1 & 0xf)
        msg = [command] + [value & 0x7f for value in data]
        self.send(msg)

    def note_off(self, note, velocity=0, ch=None):
        """Send a 'Note Off' message."""
        self.channel_message(NOTE_OFF, note, velocity)

    def note_on(self, note, velocity=127, ch=None):
        """Send a 'Note On' message."""
        self.channel_message(NOTE_ON, note, velocity)

    def pressure(self, value, note=None, ch=None):
        """Send an 'Aftertouch' or 'Channel Pressure' message.

        If a note value is provided then send an Aftertouch (Polyphonic
        pressure) message, otherwise send a Channel (mono) pressure message.

        """
        if note:
            self.channel_message(POLYPHONIC_PRESSURE, note, value, ch=ch)
        else:
            self.channel_message(CHANNEL_PRESSURE, value, ch=ch)

    def control_change(self, control, value, ch=None):
        """Send a 'Control Change' message."""
        self.channel_message(CONTROLLER_CHANGE, control, value, ch=ch)

    def program_change(self, value, bank=None, ch=None):
        """Send a 'Program Change' message.

        If *bank* is given, send 'Bank Select' LSB and MSB messages first.

        """
        if bank:
            self.control_change(BANK_SELECT_LSB, bank, ch=ch)
            self.control_change(BANK_SELECT, bank >> 7, ch=ch)

        self.channel_message(PROGRAM_CHANGE, value, ch=ch)

    def pitch_bend(self, value=0x2000, ch=None):
        """Send a 'Pitch Bend' message.

        Pitch bend is a 14-bit value, centered at 0x2000.

        """
        self.channel_message(PITCH_BEND, value, value >> 7, ch=ch)

    # System Common Messages

    def time_code(self, frame, seconds=0, minutes=0, hours=0,
                  rate=MTC_FRAME_RATE_24):
        """Send a full set of eight 'MIDI Time Code Quarter Frame' messages."""
        self.send([MTC, frame & 0xf])
        self.send([MTC, 0x10 | ((frame >> 4) & 1)])
        self.send([MTC, 0x20 | (seconds & 0xf)])
        self.send([MTC, 0x30 | ((seconds >> 4) & 3)])
        self.send([MTC, 0x40 | (minutes & 0xf)])
        self.send([MTC, 0x50 | ((minutes >> 4) & 3)])
        self.send([MTC, 0x60 | (hours & 0xf)])
        self.send([MTC, 0x70 | (rate << 1) + (1 if hours > 15 else 0)])

    def song_position(self, beats):
        """Send 'Song Position Pointer' message.

        *beats* is the number of MIDI beats since the start of the song
        (1 beat = 6 MIDI clock ticks).

        """
        self.send([SONG_POSITION_POINTER, beats & 0x7f, (beats >> 7 & 0x7f)])

    def song_select(self, song):
        """Send 'Song Select' message."""
        self.send([SONG_SELECT, song & 0x7f])

    def tuning_request(self):
        """Send 'Tuning Request' message."""
        self.send([TUNING_REQUEST])

    # System Real-Time Messages

    def timing_clock(self):
        """Send 'Timing Clock' message.

        This should be sent out 24 times per quarter note.

        """
        self.send([TIMING_CLOCK])

    def song_start(self):
        """Send 'Start' (sequence) message."""
        self.send([SONG_START])

    def song_continue(self):
        """Send 'Continue' (sequence) message."""
        self.send([SONG_CONTINUE])

    def song_stop(self):
        """Send 'Stop' (sequence) message."""
        self.send([SONG_STOP])

    def active_sensing(self):
        """Send 'Active Sensing' message."""
        self.send([ACTIVE_SENSING])

    def system_reset(self):
        """Send 'System Reset' (sequence) message."""
        self.send([SYSTEM_RESET])

    # System Exclusive Messages

    def system_exclusive(self, msg):
        if msg[0] != SYSTEM_EXCLUSIVE or msg[-1] != END_OF_EXCLUSIVE:
            raise ValueError("Invalid system exclusive message.")
        self.send(msg)

    # Controllers

    def modulation(self, value, fine=False, ch=None):
        """Send modulation control change."""
        if fine:
            self.control_change(MODULATION_WHEEL_LSB, value, ch=ch)
            self.control_change(MODULATION_WHEEL, value >> 7, ch=ch)
        else:
            self.control_change(MODULATION_WHEEL, value, ch=ch)

    def volume(self, value, fine=False, ch=None):
        """Send volume control change."""
        if fine:
            self.control_change(CHANNEL_VOLUME_LSB, value, ch=ch)
            self.control_change(CHANNEL_VOLUME, value >> 7, ch=ch)
        else:
            self.control_change(CHANNEL_VOLUME, value, ch=ch)

    def all_sound_off(self, ch=None):
        """Send 'All Sound Off' controller change message."""
        self.control_change(ALL_SOUND_OFF, 0, ch=ch)

    def reset_all_controllers(self, ch=None):
        """Send 'Reset All Controllers' controller change message."""
        self.control_change(RESET_ALL_CONTROLLERS, 0, ch=ch)

    def local_control(self, enable=True, ch=None):
        """Enable or disable local control."""
        self.control_change(LOCAL_CONTROL_ONOFF, 127 if enable else 0, ch=ch)

    def all_notes_off(self, ch=None):
        """Send 'All Notes Off' message."""
        self.control_change(ALL_NOTES_OFF, 0, ch=ch)

    def panic(self, channels=range(1,17)):
        """Reset everything and stop making noise."""
        if isinstance(channels, int):
            channels = [channels]

        for ch in channels:
            self.all_notes_off(ch=ch)
            self.all_sound_off(ch=ch)
            self.reset_all_controllers(ch=ch)
