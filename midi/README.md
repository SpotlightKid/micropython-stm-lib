MIDI Input/Output Library
=========================

The package `midi` provides support for sending and receiving MIDI messages
over a serial interface of the [pyboard] or compatible boards (for example the
STM32F4DISCOVERY board).

MIDI input and output classes are available in the separate sub-modules
`midi.midiin` and `midi.midiout` respectively, so your code can import only
what is needed.

## MIDI Input

### Usage example

    import pyb
    from midi.midiin import MidiIn

    def midi_printer(msg):
        print(tuple(msg))

    uart = pyb.UART(2, 31250)
    midiin = MidiIn(uart, callback=midi_printer)
    while True:
        midiin.poll()
        pyb.udelay(50)

### Creating a `MidiIn` Instance

Import the `MidiIn` class from the `midi.midiin` module and create an
instance of it:

    from midi.midiin import MidiIn

    midiout = MidiIn(uart)

The constructor expects an instance of a serial device class as the first
positional argument. Actually the only requirement for the passed object is
that it has `any` and `read` methods. A `TypeError` is raised otherwise. The
given object could be an instance of `pyb.UART` for serial devices or
`pyb.USB_VCP` when using the USB virtual comm port. If a serial device is used,
which is connected to a MIDI input circuit, the baud rate should be set to
31250.

You can also pass `debug=True`, which causes error messages to be printed to
`sys.stderr` when data is received, that doesn't conform to the MIDI protocol.

The remaining constructor arguments are explained in the following sections.


### The Message Callback

To handle incoming MIDI messages, you must also pass a callback function with
the `callback` argument. This function is called whenever a complete MIDI
message is received. It should expect one argument, a bytearray with the MIDI
message. The bytearray has a variable length, depending on the type of the
MIDI message.

To actually read and parse the MIDI input and trigger the callback, you must
call the `poll` method of the `MidiIn` instance regularly. You can choose the
poll interval according to the needs determined by the rest of your code, but
it should generally not be longer than it takes to receive a few characters at
the current baud rate of your serial instance. For a standard MIDI interface
with a 31250 baud rate the time to receive one byte is about 0.3 milliseconds.


### Soft Thru

If you pass `softthru=True` to the `MidiIn` contructor, the serial device
instance you pass must also have a `write` method, which accepts one argument
of type `bytes`. Each byte received via the `read` method of the device is then
passed to the `write` method unfiltered and unaltered. This allows you to
use the MIDI output as a soft MIDI thru. Please note that this introduces a
delay of the MIDI messages passed through, the magnitude of which depends on
your poll interval.

Since bytes read from MIDI in are passed immediately, without parsing, one by
one to the MIDI out, the `softthru` option will not work correctly if you also
send MIDI messages with the `MidiOut` class. To keep the proper sequence of
MIDI bytes, the MIDI input and output have to be logically merged in this case.
This library currently does not provide support for MIDI merging.


### Ignoring Active Sense, Timing Clock or System Exclusive Messages

Normally the callback is called for every received message, regardless of its
type. You can, however, enable filtering of certain message types, so that they
are dropped and never reach your callback.

To enable filtering, call the `ignore_types` method of your `MidiIn` instance
and pass `active_sensing=True`, `clock=True` and/or `sysex=True` to filter out
Active Sensing (0xFE), Timing Clock (0xF8) or System Exclusive (0xF0 ... 0xF7)
Messages respectively. You can enable/disable all these filters at once or
selectively.


## MIDI Output

### Usage example

    import pyb
    from midi.midiout import MidiOut

    uart = pyb.UART(2, baudrate=31250)
    midiout = MidiOut(uart)

    midiout.program_change(0)  # Acoustic Piano per General MIDI standard
    pyb.delay(100)

    for note in (60, 64, 67, 72):
        midiout.note_on(note, velocity=100)
        pyb.delay(250)
        midiout.note_off(note)  # velocity defaults to 0

### Creating a `MidiOut` Instance

Import the `MidiOut` class from the `midi.midiout` module and create an
instance of it:

    from midi.midiout import MidiOut

    midiout = MidiOut(uart)

The constructor expects an instance of a serial device class as the first
positional argument. Actually the only requirement for the passed object is
that it has a `write` method, which accepts one argument of type `bytes`. A
`TypeError` is raised otherwise. The given object could be an instance of
`pyb.UART` for serial devices or `pyb.USB_VCP` when using the USB virtual comm
port. If a serial device is used, which is connected to a MIDI output circuit,
the baud rate should be set to 31250.

You can also optionally pass a MIDI channel number as a second parameter to the
constructor. This can be retrieved and set via the `channel` property of the
instance and is used as the default channel for channel messages send via this
instance. It must be an integer between 1 and 16 and a `ValueError` is raised
when the given channel is out of range or you try to set the `channel` property
to an invalid value.


### Sending MIDI Messages

The generic method to send a MIDI message is `send` and it takes the message to
send as a single argument, which must be an iterable yielding integers, e.g.
a `tuple` or `list` of integers, a `bytes` or `bytearray` instance or similar:

    # send a Note On message on channel 10 for note 36, velocity 100
    midiout.send([0x99, 36, 100])

The `MidiOut` class provides convenience methods for sending all standard types
of MIDI messages and also for the most common controller types.

#### Channel Messages

All channel message methods accept an optional keyword argument `ch` to specify
the MIDI channel of the message. It defaults to the value of the `channel`
property of the `MidiOut` instance.

    channel_message(command, *data[, ch=None])

The generic `channel_message` method is mainly used an internal helper method
by the other methods listed below. The `command` parameter must be a MIDI
channel message status byte (`0x80..0xE0`). The lower nibble of `command`,
where the MIDI channel is encoded, is ignored and taken either from the `ch`
keyword parameter or the `channel` instance property as described above.
Additional positional parameters are used as the data bytes of the MIDI message
and must be integers, which will be OR'ed with `0x7F` to ensure they have a
value range `0..127`.

All the parameters of the methods listed below in this section have a value
range of `0..127`, except the `ch` parameter (`1..16`) and where noted
otherwise.

Note On / Off:

    midiout.note_on(note[, velocity])
    midiout.note_off(note[, velocity])

Pitch Bend:

    # -8191 <= value <= 8192
    midiout.pitch_bend(value)

Mono and Poly Pressure:

    # Send a channel pressure message:
    midiout.pressure(value)
    # Send a poly pressure message:
    midiout.pressure(value, note)

Program Change and Bank Select:

    # Send a program change message:
    midiout.program_change(program)
    # Send a bank select MSB (CC #0) followed by a program change message:
    midiout.program_change(program, msb=0)
    # Send a bank select LSB (CC #32) followed by a program change message:
    midiout.program_change(program, lsb=0)
    # Send a bank select MSB (CC #0, value 1) and LSB (CC #32, value 0)
    # followed by a program change message (0 <= bank <= 16383):
    midiout.program_change(program, bank=128)

Control Change:

    midiout.control_change(controller, value)

The `midi.constants` module defines constants for all standard controller
numbers. These constants are also imported into the namespace of the
`midi.midiout` module. This allows you to send control change messages with
controller numbers, for which no convenience method has been provided, but keep
the code readable:

    midiout.control_change(LEGATO_ONOFF, 127)

High-Resolution Controllers:

The `control_change` method and each of the standard controller message methods
below accept an optional boolean keyword parameter `lsb`, which defaults to
`False`. If it is `True`, `value` is interpreted as a 14-bit value and two
control change messagess are sent. First one with the given controller number
and the upper 7 bits of `value` as the control value, and then another with the
given controller number plus 32 and the lower 7 bits of `value` as the control
value. `lsb` is ignored for controller numbers `>= 32`.

Standard Controllers:

    # Send a bank select MSB (CC #0):
    midiout.bank_select(msb=0)
    # Send a bank select LSB (CC #32):
    midiout.bank_select(lsb=0)
    # Send a bank select MSB (bank >> 7) and a bank select LSB (bank & 0x7f):
    midiout.bank_select(bank)

    midiout.modulation(value)         # CC #1
    midiout.breath_controller(value)  # CC #2
    midiout.foot_controller(value)    # CC #4
    midiout.portamento_time(value)    # CC #5
    midiout.data_entry(value)         # CC #6
    midiout.volume(value)             # CC #7
    midiout.balance(value)            # CC #8
    midiout.pan(value)                # CC #10
    midiout.expression(value)         # CC #11


### Channel Mode Messages

    midiout.all_sound_off()
    midiout.reset_all_controllers()
    midiout.all_notes_off()

    # Send a local control message with value 127 (on):
    midiout.local_control()
    # Send a local control message with value 0 (off):
    midiout.local_control(False)

    # Send an omni mode on message:
    midiout.omni_mode()
    # Send an omni mode off message:
    midiout.omni_mode(False)

    # Send a poly mode on message:
    midiout.poly_mode()
    # Send a mono mode on message:
    midiout.poly_mode(False)

    # Send all notes off, all sound off and reset all controllers on
    # all channels:
    midiout.panic()
    # ... or on the given list of channels:
    midiout.panic(range(1,4))
    # ... or only on given channel:
    midiout.panic(16)


#### System Common Messages

    midiout.song_position(beat)
    midiout.song_select(song)
    midiout.tuning_request()
    midiout.time_code(frame, seconds, minutes, hours[, rate])

For `time_code`, the `rate` parameter must be one of the constants
`MTC_FRAME_RATE_24`, `MTC_FRAME_RATE_25`, `MTC_FRAME_RATE_30_DROP` and
`MTC_FRAME_RATE_30` from the `midi.constants` module and defaults to
`MTC_FRAME_RATE_24`.


#### System Real-Time Messages

    midiout.timing_clock()
    midiout.song_start()
    midiout.song_continue()
    midiout.song_stop()
    midiout.active_sensing()
    midiout.system_reset()

#### System Exclusive Messages

System exclusive (sysex) messages consist of a sequence of bytes with an
arbitrary length, where the first byte has the value `0xF0` and the last one
`0xF7`. All bytes in between must have a value `<= 0x7F`. You can just use the
`send` method to send sysex or use the `system_exclusive` method, which
checks whether the given message (which must be a real sequence, not an
iterator) conforms to these rules and raises a `ValueError` otherwise.

    midiout.system_exclusive([0xF0, 0x7E, 0, 6, 1, 0xF7])


[pyboard]: http://docs.micropython.org/en/latest/pyboard/quickref.html
