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

* Connect the GND pin of the encoder to ground.
* Connect the CLK pin of the encoder to a GPIO pin on the board
  (e.g. 'X11' on the pyboard).
* Connect the DT pin of the encoder to another GPIO on the board
  (e.g. 'X12' on the pyboard).

If you configure the input pins with the internal pull-up resistors turned on,
you don't need to connect 5V from the board to anything, since the input pins
will provide the current for the switches in the encoder to function. Without
the pull-up resistors, connect 5V or 3V3 from the board to the plus pin of the
encoder.

Usage
-----

When everything is hooked up, use the `Encoder` class like this:

    from machine import sleep_ms
    from encoder import Encoder  # or from pyb_encoder import Encoder

    e = Encoder('X11', 'X12')  # optional: add pin_mode=Pin.PULL_UP
    lastval = e.value

    while True:
        val = e.value
        if lastval != val:
            lastpos = val
            print(val)
        sleep_ms(100)


Clicks and Acceleration
-----------------------

Normally the encoder value is de-/increased by one for every encoder pulse.
Most encoders generate several pulses per dedent ("click"). You can pass the
`clicks` keyword when instantiating the `Encoder` class to set the number of
pulses per dedent. A common value is four. This will result in an increment /
decrement of one for every click with no acceleration.

If you have a large value range (you can set the range with the `min_val` and
`max_val` keyword arguments), scrolling from one end of the range to the other
can be very cumbersome. You can enable acceleration by passing a positive
integer to the `accel` keyword argument. The proper value depends on value
range and the type of the encoder, but usually low one-digit numbers like 3-5
work well. With acceleration enabled the increment/decrement per click increases
the faster your turn the encoder. You can still make fine adjustment by turning
the encoder slowly.


[pyboard]: http://docs.micropython.org/en/latest/pyboard/quickref.html
[blog post]: https://www.circuitsathome.com/mcu/reading-rotary-encoder-on-arduino
