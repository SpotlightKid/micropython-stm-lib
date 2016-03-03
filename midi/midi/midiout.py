# -*- coding: utf-8 -*-
"""MicroPython MIDI output library."""

from .constants import *


class MidiOut:
    """MIDI output class."""

    def __init__(self, device, ch=1):
        if not hasattr(device, 'write'):
            raise TypeError("device instance must have a 'write' method.")

        self.device = device
        self.channel = ch

    def __repr__(self):
        return '<MidiOut: device={} channel={}>'.format(
            self.device, self.channel)

    @property
    def channel(self):
        return self._ch

    @channel.setter
    def channel(self, ch):
        if not 1 <= ch <=16:
            raise ValueError('Channel must be an integer between 1..16.')
        self._ch = ch

    def send(self, msg):
        """Send a MIDI message to the serial device."""
        return self.device.write(bytes(msg))

    # Channel Mode Messages

    def channel_message(self, command, *data, ch=None):
        """Send a MIDI channel mode message to the serial device."""
        command = (command & 0xf0) | ((ch if ch else self.channel) - 1 & 0xf)
        msg = [command] + [value & 0x7f for value in data]
        self.send(msg)

    def note_off(self, note, velocity=0, ch=None):
        """Send a 'Note Off' message."""
        self.channel_message(NOTE_OFF, note, velocity, ch=ch)

    def note_on(self, note, velocity=127, ch=None):
        """Send a 'Note On' message."""
        self.channel_message(NOTE_ON, note, velocity, ch=ch)

    def pressure(self, value, note=None, ch=None):
        """Send an 'Aftertouch' or 'Channel Pressure' message.

        If a note value is provided then send an Aftertouch (Polyphonic
        pressure) message, otherwise send a Channel (mono) pressure message.

        """
        if note is None:
            self.channel_message(CHANNEL_PRESSURE, value, ch=ch)
        else:
            self.channel_message(POLYPHONIC_PRESSURE, note, value, ch=ch)

    def control_change(self, control, value, lsb=False, ch=None):
        """Send a 'Control Change' message."""
        lsb = lsb and control < 32
        self.channel_message(CONTROLLER_CHANGE, control,
                             value >> 7 if lsb else value, ch=ch)

        if lsb:
            self.channel_message(CONTROLLER_CHANGE, control + 32, value, ch=ch)

    def program_change(self, program, bank=None, msb=None, lsb=None, ch=None):
        """Send a 'Program Change' message."""
        self.bank_select(bank, msb, lsb, ch)
        self.channel_message(PROGRAM_CHANGE, program, ch=ch)

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
        if not msg or msg[0] != SYSTEM_EXCLUSIVE:
            raise ValueError("System exclusive message must start with 0xF0.")
        if msg[-1] != END_OF_EXCLUSIVE:
            raise ValueError("System exclusive message must end with 0xF7.")
        for value in msg[1:-1]:
            if not 0 <= value <= 127:
                raise ValueError(
                    "System exclusive message data byte out of range 0-127.")
        self.send(msg)

    # Controllers

    def bank_select(self, bank=None, msb=None, lsb=None, ch=None):
        """Send 'Bank Select' MSB and/or LSB 'Control Change' message.

        If *bank* is given, send 'Bank Select' LSB and MSB messages. The bank
        select MSB and LSB can also be given separately with the *msb* and
        *lsb* keyword arguments or only one of either. *bank* takes precedence
        over *msb* and *lsb* and all are optional.

        """
        if bank is not None:
            msb, lsb = bank >> 7, bank

        if msb is not None:
            self.control_change(BANK_SELECT, msb, ch=ch)

        if lsb is not None:
            self.control_change(BANK_SELECT_LSB, lsb, ch=ch)

    def modulation(self, value, lsb=False, ch=None):
        """Send modulation control change."""
        self.control_change(MODULATION_WHEEL, value, lsb, ch)

    def breath_controller(self, value, lsb=False, ch=None):
        """Send breath controller control change."""
        self.control_change(BREATH_CONTROLLER, value, lsb, ch)

    def foot_controller(self, value, lsb=False, ch=None):
        """Send foot controller control change."""
        self.control_change(FOOT_CONTROLLER, value, lsb, ch)

    def portamento_time(self, value, lsb=False, ch=None):
        """Send portamento time control change."""
        self.control_change(PORTAMENTO_TIME, value, lsb, ch)

    def data_entry(self, value, lsb=False, ch=None):
        """Send data entry control change."""
        self.control_change(DATA_ENTRY, value, lsb, ch)

    def volume(self, value, lsb=False, ch=None):
        """Send volume control change."""
        self.control_change(CHANNEL_VOLUME, value, lsb, ch)

    def balance(self, value, lsb=False, ch=None):
        """Send balance control change."""
        self.control_change(BALANCE, value, lsb, ch)

    def pan(self, value, lsb=False, ch=None):
        """Send pan control change."""
        self.control_change(PAN, value, lsb, ch)

    def expression(self, value, lsb=False, ch=None):
        """Send expression controller control change."""
        self.control_change(EXPRESSION_CONTROLLER, value, lsb, ch)

    def all_sound_off(self, ch=None):
        """Send 'All Sound Off' controller change message."""
        self.control_change(ALL_SOUND_OFF, 0, ch=ch)

    def reset_all_controllers(self, ch=None):
        """Send 'Reset All Controllers' controller change message."""
        self.control_change(RESET_ALL_CONTROLLERS, 0, ch=ch)

    def local_control(self, on=True, ch=None):
        """Enable or disable local control."""
        self.control_change(LOCAL_CONTROL_ONOFF, 127 if on else 0, ch=ch)

    def all_notes_off(self, ch=None):
        """Send 'All Notes Off' message."""
        self.control_change(ALL_NOTES_OFF, 0, ch=ch)

    def omni_mode(self, on=True, ch=None):
        self.control_change(OMNI_MODE_ON if on else OMNI_MODE_OFF, 0, ch=ch)

    def poly_mode(self, on=True, ch=None):
        self.control_change(POLY_MODE_ON if on else MONO_MODE_ON, 0, ch=ch)

    def panic(self, channels=range(1,17)):
        """Reset everything and stop making noise."""
        if isinstance(channels, int):
            channels = [channels]

        for ch in channels:
            self.all_notes_off(ch=ch)
            self.all_sound_off(ch=ch)
            self.reset_all_controllers(ch=ch)
