MicroPython-STM-Lib
===================

A collection of Python modules and examples for [MicroPython], targeted mainly
for STM32F4-based boards, like the [STM32F4DISCOVERY] board or the original
[pyboard]. Most modules also work on the MicroPython unix port or even other
bare-metal ports, e.g. the *esp8266* port.

Currently, this collection contains:

* `accel/` - a fixed version of [staccel.py] from the main MicroPython repo
  including examples.
* `encoder/` - a library for reading a rotary encoder connected to two digital
  input pins, including examples. Features gray code error checking, making
  software or hardware debouncing uneccessary in most cases.
* `lcd/` - a library for interfacing with a HD44780-compatible LCD controller,
  including examples.
* `midi/` - a library for receiving and sending MIDI data via the UARTs or the
  USB virtual serial interface, including examples.
* `picoredis/ ` - A very mimimal Redis client library (not only) for
  MicroPython.
* `spiflash` - A module for using Winbond W25Q* SPI-attached flash memory chips
  with MicroPython (adapted from code found in
  [this repo](https://github.com/manitou48/pyboard)).
* `spimaster/` - a rudmentary library to communicate via SPI with an ESP8266
  module as the SPI slave, controlled by an Arduino sketch using the [SPISlave]
  library.


Author
------

Except where otherwise noted, these modules and examples were written by
Christopher Arndt.


License
-------

Except where otherwise noted, the code is freely usable and distributable
under the MIT License.


[micropython]: http://micropython.org/
[stm32f4discovery]: http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/PF252419
[pyboard]: https://store.micropython.org/#/products/PYBv1_1
[staccel.py]: https://github.com/micropython/micropython/blob/master/ports/stm32/boards/STM32F4DISC/staccel.py
[spislave]: https://github.com/esp8266/Arduino/tree/master/libraries/SPISlave
