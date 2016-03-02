import pyb

from mid.midiin import MidiIn


def midi_printer(msg):
    print(tuple(msg))

def loop(midiin):
    while True:
        midiin.poll()
        pyb.udelay(500)

uart = py.UART(2, 31250)
midiin = MidiIn(uart, callback=midi_printer)
loop(midiin)
