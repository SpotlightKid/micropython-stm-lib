Micropython-STM-lib
===================

A collection of Python modules and examples for [MicroPython][] running on an
[STM32F4DICOVERY][] board or the original [pyboard][] including examples.

Currently, this collection contains:

* `accel/` - a fixed version of [staccel.py][] from the main MicroPython repo
  including examples.
* `encoder/` - a library for reading a rotary encoder connected to two digital
  input pins, including examples. Features gray code error checking, making
  software or hardware debouncing uneccessary in most cases.
* `lcd/` - a library for interfaceing with a HD44780-compatible LCD controller,
  including examples.
* `midi/` - a library for receiving and sending MIDI data via the UARTs or the
  USB virtual seriell interface, including examples.


Author
------

Except where otherwise noted, these modules and examples were written by
Christopher Arndt.


License
-------

Except where otherwise noted, the code is freely usable and distributable
under the MIT License.


[micropython]: http://micropython.org
[stm32f4dicovery]: http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/PF252419
[pyboard]: https://micropython.org/store/#/products/PYBv1_0
[staccel.py]: https://github.com/micropython/micropython/blob/master/stmhal/boards/STM32F4DISC/staccel.py

