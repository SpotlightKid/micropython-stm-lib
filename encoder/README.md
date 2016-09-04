Rotary Encoder Library
======================

The file `encoder.py` provides a module to read a rotary encoder connected
to a MicroPython board. The class `encoder.Encoder` works with ESP-8266 boards.
The file `pyb_encoder.py` provides a subclass (`pyb_encoder.Encoder`), which
works with the [pyboard] or any board using the stmhal port (for example a
STM32F4DISCOVERY board).

The rotary encoder needs to connect to two digital input pins of of the board,
for which external interrupts can be enabled. The code employs gray code error
checking using the technique described in this [blog post], so no further
hardware or software debouncing is needed and the library works well even with
cheap encoders, which usually have switches with lots of bouncing.


Encoder Hookup
--------------

* Connect the middle pin of the encoder to ground.
* Connect one of the outer pins of the encoder to PA0 on the STM32F4.
* Connect the other outer pin of the encoder to PA1 on the STM32F4.

If you configure the input pins with the internal pull-up resistors turned on,
you don't need to connect 5V from the board to anything, since the input pins
will provide the current for the switches in the encoder to function. Without
the pull-up resistors, connect 5V or 3V3 from the board to the plus pin of the
encoder.

Then use the `Encoder` class like this:

    from machine import sleep_ms
    from encoder import Encoder

    e = Encoder('A0', 'A1')  # optional: add pin_mode=Pin.PULL_UP
    lastval = e.value

    while True:
        val = e.value
        if lastval != val:
            lastpos = val
            print(val)
        sleep_ms(100)


[pyboard]: http://docs.micropython.org/en/latest/pyboard/quickref.html
[blog post]: https://www.circuitsathome.com/mcu/reading-rotary-encoder-on-arduino
