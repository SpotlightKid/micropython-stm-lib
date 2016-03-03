"""Playback from a set of simple tunes via MIDI.

MIDI output circuit:

https://www.midi.org/articles/midi-electrical-specifications

1. 5V (3.3V) connected to MIDI output socket pin 4 via 220 (35) ohm resistor
2. GND connected to MIDI output socket pin 2
3. UART2 TX pin connected to MIDI output socket pin 5 via 220 (10) ohm resistor

Switch buttons:

4. A push button between pin PC0 and GND
5. A push button between pin PC1 and GND

"""

from pyb import delay, LED, Pin, Switch, UART
from midi.midiout import MidiOut
from tunes import TUNES


TUNENAMES = ['DADADADUM', 'ENTERTAINER', 'PRELUDE', 'ODE', 'NYAN', 'RINGTONE',
    'FUNK', 'BLUES', 'BIRTHDAY', 'WEDDING', 'FUNERAL', 'PUNCHLINE', 'PYTHON',
    'BADDY', 'CHASE', 'WAWAWAWAA', 'JUMP_UP', 'JUMP_DOWN', 'POWER_UP',
    'POWER_DOWN']

PROGRAMS = [
    0,   # Acoustic Grand Piano
    49,  # String Esemble
    25,  # Acoustic Guitar
    35,  # Picked Electric Bass
    10,  # Glockenspiel
]

NOTES = {
    'c': 0,
    'd': 2,
    'e': 4,
    'f': 5,
    'g': 7,
    'a': 9,
    'b': 11,
}

BLINK_DELAY = 200


def play(midi, notes, led, bpm=120):
    duration = octave = 4
    mpt = 60000 / bpm / 4

    try:
        for note in notes:
            try:
                note, duration = note.split(':')
                duration = int(duration)
            except:
                pass

            try:
                octave = int(note[-1])
                note = note[:-1]
            except (ValueError, IndexError):
                pass

            note = note.lower()
            midinote = NOTES.get(note[0])

            if midinote is not None:
                if note.endswith('#'):
                    midinote += 1
                elif len(note) > 1 and note.endswith('b'):
                    midinote -= 1

                midinote = max(0, min(127, midinote + 12 * octave))
                midi.note_on(midinote, 96)
                led.on()

            delay(int(duration * mpt))

            if midinote is not None:
                midi.note_off(midinote)
                led.off()

        # make sure led and last note is turned off
        if midinote is not None:
            led.off()
            midi.note_off(midinote)
    except Exception:
        # Send all sound off to prevent hanging notes
        midi.control_change(0x78, 0)


def main():
    # Initialize UART for MIDI
    uart = UART(2, baudrate=31250)
    midi = MidiOut(uart)
    button1 = Switch()
    button2 = Pin('PC0', Pin.IN, Pin.PULL_UP)
    button3 = Pin('PC1', Pin.IN, Pin.PULL_UP)
    led1 = LED(1)
    led2 = LED(2)
    led3 = LED(3)
    tune = program = 0

    # send a PROGRAM CHANGE to set instrument to #0 (Grand Piano)
    midi.program_change(program)

    while True:
        if button1():
            # When button 1 is pressed, play the current tune
            play(midi, TUNES[TUNENAMES[tune]], led1)
            led1.off()
        if not button2():
            # When button 2 is pressed, select the next of the tunes
            led2.on()
            tune = (tune+1) % len(TUNENAMES)
            delay(BLINK_DELAY)
            led2.off()
        if not button3():
            # When button 3 is pressed, change to next program (instrument)
            led3.on()
            program = (program+1) % len(PROGRAMS)
            midi.program_change(PROGRAMS[program])
            delay(BLINK_DELAY)
            led3.off()

        delay(200)
