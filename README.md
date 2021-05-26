MicroPython-STM-Lib
===================

A collection of Python modules and examples for [MicroPython], targeted mainly
at STM32F4-based boards, like the [STM32F4DISCOVERY] board or the original
[pyboard]. Most modules also work on the MicroPython unix port or even other
bare-metal ports, e.g. the *esp8266* or *esp32* port.

Currently, this collection contains:

* [accel](./accel/) - a fixed version of [staccel.py] from the main MicroPython
  repo including examples.
* [encoder](./encoder/) - a library for reading a rotary encoder connected to
  two digital input pins, including examples. Features gray code error
  checking, making software or hardware debouncing uneccessary in most cases.
* [lcd](./lcd/) - a library for interfacing with a HD44780-compatible LCD
  controller, including examples.
* [midi](midi/) - a library for receiving and sending MIDI data via the UARTs
  or the USB virtual serial interface, including examples.
* [mrequests] - an evolution of `urequests` from `micropython-lib`
  with improvements and new features.
* [netconfig](./netconfig/) - simple WiFi or ethernet network setup from JSON
  configuration files.
* [picoredis] - a very mimimal Redis client library (not only)
  for MicroPython.
* [spiflash](./spiflash/) - a module for using Winbond W25Q* SPI-attached flash
  memory chips with MicroPython (adapted from code found in [this repo]).
* [spimaster](./spimaster/) - a rudimentary library to communicate via SPI with
  an ESP826 module as the SPI slave, which runs an Arduino sketch using the
  [SPISlave] library.


Author
------

Except where otherwise noted, these modules and examples were written by
Christopher Arndt.


License
-------

Except where otherwise noted, the code is freely usable and distributable
under the [MIT License].


[micropython]: http://micropython.org/
[mit license]: http://opensource.org/licenses/MIT
[mrequests]: https://github.com/SpotlightKid/mrequests/tree/master
[picoredis]: https://github.com/SpotlightKid/picoredis/tree/master
[pyboard]: https://store.micropython.org/#/products/PYBv1_1
[spislave]: https://github.com/esp8266/Arduino/tree/master/libraries/SPISlave
[staccel.py]: https://github.com/micropython/micropython/blob/master/ports/stm32/boards/STM32F4DISC/staccel.py
[stm32f4discovery]: http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/PF252419
[this repo]: https://github.com/manitou48/pyboard
