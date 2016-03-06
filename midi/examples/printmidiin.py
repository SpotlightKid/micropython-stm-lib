import pyb

from midi.midiin import MidiIn


def midi_printer(msg):
    print(tuple(msg))

def loop(midiin):
    while True:
        midiin.poll()
        pyb.udelay(50)

uart = pyb.UART(2, 31250)
midiin = MidiIn(uart, callback=midi_printer)
loop(midiin)
