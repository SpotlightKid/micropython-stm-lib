"""Communicate via SPI with an ESP8266 module.

The Micropython board is the SPI master and the ESP8266 the slave. The HSPI
port of the ESP822 is used, which is implemented in hardware and controlled
by an Arduino-for-ESP8266 sketch, which uses the SPISlave library.

https://github.com/esp8266/Arduino/tree/master/libraries/SPISlave

To test, wire the two boards together like this:

+----------+-----------------------+-------------------+
| Function | Pyboard / STM32F4DISC | ESP8266 / NodeMCU |
+==========+=======================+===================+
| SS       | X5 / (P)A4            | 15 / D8           |
+----------+-----------------------+-------------------+
| SCK      | X6 / (P)A5            | 14 / D5           |
+----------+-----------------------+-------------------+
| MISO     | X7 / (P)A6            | 12 / D6           |
+----------+-----------------------+-------------------+
| MOSI     | X8 / (P)A7            | 11 / D7           |
+----------+-----------------------+-------------------+
| GND      | GND                   | GND               |
+----------+-----------------------+-------------------+

"""

from pyb import Pin, SPI


class SpiMaster:
    def __init__(self, bus=1, baudrate=328125, polarity=0, phase=0, ss='A4'):
        self.ss = Pin(ss, Pin.OUT)
        self.ss.high()
        self.spi = SPI(bus, SPI.MASTER, baudrate=baudrate, polarity=polarity,
                       phase=phase)
        self.msgbuf = bytearray(32)
        self.status = bytearray(4)

    def write_status(self, status):
        self.ss.low()
        self.spi.send(0x01)
        self.spi.send(status & 0xFF)
        self.spi.send((status >> 8) & 0xFF)
        self.spi.send((status >> 16) & 0xFF)
        self.spi.send((status >> 24) & 0xFF)
        self.ss.high()

    def read_status(self):
        self.ss.low()
        self.spi.send(0x04)
        self.spi.recv(self.status)
        self.ss.high()
        return (
            self.status[0] |
            (self.status[1] << 8) |
            (self.status[2] << 16) |
            (self.status[3] << 24)
        )

    def read_data(self):
        self.ss.low()
        self.spi.send(0x03)
        self.spi.send(0x00)
        self.spi.recv(self.msgbuf)
        self.ss.high()
        return self.msgbuf

    def read_msg(self, encoding='utf-8'):
        return bytes(self.read_data()).strip('\0').decode(encoding)

    def write_data(self, data):
        self.msgbuf[:] = data[:32] + b'\0' * (32 - len(data[:32]))
        self.ss.low()
        self.spi.send(0x02)
        self.spi.send(0x00)
        self.spi.send(self.msgbuf)
        self.ss.high()


if __name__ == '__main__':
    # Example usage
    from time import ticks_diff, ticks_ms
    #from spimaster import SpiMaster

    def timeit():
        spi = SpiMaster(1, baudrate=int(pyb.freq()[3] / 16))
        start = ticks_ms()

        for i in range(2 ** 10):
            spi.write_data(b'abcdefgh' * 4)
            spi.read_data()

        print("Millisecond ticks elapsed: %i" % ticks_diff(ticks_ms(), start))

    timeit()
