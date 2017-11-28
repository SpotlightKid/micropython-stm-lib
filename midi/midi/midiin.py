# -*- coding: utf-8 -*-
"""MicroPython MIDI input library."""

from .constants import *


class MidiIn:
    """MIDI input class."""

    def __init__(self, device, callback=None, debug=False, softthru=False):
        if not hasattr(device, 'any'):
            raise TypeError("device instance must have a 'any' method.")

        if not hasattr(device, 'read'):
            raise TypeError("device instance must have a 'read' method.")

        if softthru and not hasattr(device, 'write'):
            raise TypeError("device instance must have a 'write' method if "
                            "soft thru is enabled.")

        self.device = device
        self.callback = callback
        self.debug = debug
        self.softthru = softthru
        self._msgbuf = None
        self._status = None
        self.ignore_types()

    def __repr__(self):
        return '<MidiIn: device={} callback={}>'.format(
            self.device, 'yes' if callable(self.callback) else 'no')

    def poll(self):
        """Poll the input device for newly received MIDI messages.

        Calls the callback function for any received complete message.

        """
        msgs = self._read()

        if msgs and self.callback:
            for msg in msgs:
                self.callback(msg)

    def ignore_types(self, active_sensing=False, clock=False, sysex=False):
        """Activate filter for certain event types.

        To improve performance, Active Sensing (0xFE), Timing Clock (0xF8) or
        System Exclusive (0xF0 ... 0xF7) Messages can be filtered out, so they
        are dropped and do not trigger the input callback function.

        Pass ``active_sensing=True``, ``clock=True`` and/or ``sysex=True`` to
        enable the filter for the respective event types.

        """
        self._ignore_active_sense = active_sensing
        self._ignore_clock = clock
        self._ignore_sysex = sysex

    def _error(self, msg, *args):
        if self.debug:
            import sys
            print(msg % args, file=sys.stderr)

    def _read(self):
        """Read data from input device and buffer incomplete messages.

        Returns list of complete messages received. Messages are bytearray
        instances.

        """
        msgs = []
        while self.device.any():
            data = self.device.read(1)[0]

            if self.softthru:
                # pass byte from MIDI in through to MIDI out
                self.device.write(bytes([data]))

            if data & 0x80:
                # A status byte
                if TIMING_CLOCK <= data <= SYSTEM_RESET:
                    # System real-time message
                    if data == ACTIVE_SENSING and self._ignore_active_sensing:
                        continue
                    elif data == TIMING_CLOCK and self._ignore_clock:
                        continue
                    elif data != 0xFD:
                        msgs.append(bytearray([data]))
                    else:
                        self._error("Read undefined system real-time status "
                                    "byte 0x%0X.", data)
                elif data == SYSTEM_EXCLUSIVE:
                    # Start of sysex message
                    self._status = SYSTEM_EXCLUSIVE
                    if self._ignore_sysex:
                        self._msgbuf = None
                    else:
                        self._msgbuf = bytearray([data])
                elif data == END_OF_EXCLUSIVE:
                    # End of sysex message
                    if self._msgbuf and not self._ignore_sysex:
                        self._msgbuf.append(data)
                        msgs.append(self._msgbuf)

                    self._msgbuf = None
                    self._status = None
                elif MIDI_TIME_CODE <= data <= TUNING_REQUEST:
                    # System common message
                    self._status = None
                    self._msgbuf = None

                    if data == TUNING_REQUEST:
                        msgs.append(bytearray([data]))
                    elif data <= SONG_SELECT:
                        self._msgbuf = bytearray([data])
                    else:
                        self._error("Read undefined system common status byte "
                                    "0x%0X.", data)
                else:
                    # Channel mode/voice message
                    self._status = data
                    self._msgbuf = bytearray([data])
            else:
                if self._status == SYSTEM_EXCLUSIVE and self._ignore_sysex:
                    continue

                # A data byte
                if self._status and not self._msgbuf:
                    # Running status assumed
                    self._msgbuf = bytearray([self._status])

                if not self._msgbuf:
                    self._error("Read unexpected data byte 0x%0X." % data)
                    continue

                self._msgbuf.append(data)

                if (self._status != SYSTEM_EXCLUSIVE and
                        (len(self._msgbuf) == 3 or self._msgbuf[0] & 0xF0 in
                         (PROGRAM_CHANGE, CHANNEL_PRESSURE, MTC, SPP))):
                    msgs.append(self._msgbuf)
                    self._msgbuf = None

        return msgs
