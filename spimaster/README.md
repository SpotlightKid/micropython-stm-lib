SPI Master
==========

Communicate via SPI with an ESP8266 module.

The Micropython board is the SPI master and the ESP8266 the slave. The HSPI
port of the ESP822 is used, which is implemented in hardware and controlled
by an Arduino-for-ESP8266 sketch, which uses the [SPISlave] library.

To test, wire the two boards together like this:

|  Function | Pyboard / STM32F4DISC | ESP8266 / NodeMCU |
| --------- | --------------------- | ----------------- |
| SS        | X5 / (P)A4            | 15 / D8           |
| SCK       | X6 / (P)A5            | 14 / D5           |
| MISO      | X7 / (P)A6            | 12 / D6           |
| MOSI      | X8 / (P)A7            | 11 / D7           |
| GND       | GND                   | GND               |

On the ESP8266 use the Arduino IDE to compile & upload the
"SPISlave/SPISlave_Test.ino" sketch from the examples included with the
Arduino core for ESP8266.

You can test and benchmark the communication on your micropython board with
the following code:

    import pyb
    from time import ticks_diff, ticks_ms
    from spimaster import SpiMaster

    def timeit():
        spi = SpiMaster(1, baudrate=int(pyb.freq()[3] / 16))
        start = ticks_ms()

        for i in range(2 ** 10):
            spi.write_data(b'abcdefgh' * 4)
            spi.read_data()

        print("Millisecond ticks elapsed: %i" % ticks_diff(ticks_ms(), start))

    timeit()


[spislave]: https://github.com/esp8266/Arduino/tree/master/libraries/SPISlave
