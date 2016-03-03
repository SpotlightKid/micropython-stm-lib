"""Play a drum pattern via MIDI.

MIDI output circuit:

https://www.midi.org/articles/midi-electrical-specifications

1. 5V (3.3V) connected to MIDI output socket pin 4 via 220 (35) ohm resistor
2. GND connected to MIDI output socket pin 2
3. UART2 TX pin connected to MIDI output socket pin 5 via 220 (10) ohm resistor

"""

from pyb import delay, Switch, UART
from midi.midiout import MidiOut
from drumseq import Pattern, Sequencer


PATTERN = """
# Rosanna Shuffle
# about 124 bpm (for a real tempo of 93 bpm)
#  1..|..|..|..2..|..|..|..
36 x....m...x.....m..s..... Bassdrum
40 .+-.+-m+-.+-.+-.+-m+-.++ Snare 2
42 x-sx-sx-sx-sx-sx-sx-sx-s Closed Hi-hat
"""


def main():
    switch = Switch()

    while not switch():
        delay(200)

    # Initialize UART for MIDI
    uart = UART(2, baudrate=31250)
    midi = MidiOut(uart)
    seq = Sequencer(midi, bpm=124)
    seq.play(Pattern(PATTERN), kit=9)
