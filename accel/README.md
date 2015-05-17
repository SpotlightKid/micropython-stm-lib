STAcccel
========

This is a fixed version of the [staccel.py] module from the official
MicroPython repository, which is also under the MIT License.

The call to `STAccel.read_id()` in `STAccel.__init__()` always returns 255
instead of the correct value 63. In fact, the first read on the SPI bus after
creating the pyb.SPI instance seems to always return 255.

I fixed this by just reading the ID twice and the second time succeeds.

See also this [forum topic].

[staccel.py]: https://github.com/micropython/micropython/blob/master/stmhal/boards/STM32F4DISC/staccel.py
[forum topic]: http://forum.micropython.org/viewtopic.php?f=2&t=595
