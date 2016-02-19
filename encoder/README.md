Rotary Encoder Library
======================

The file `encoder.py` provides a module to read a rotary encoder connected
to two digital input pins of a [pyboard] or an STM32F4DISCOVERY board via
external interrupts.

It uses gray code error checking using the technique described in this [blog
post], so usually hardware or software debouncing is not needed.


Encoder Hookup
--------------

* Connect the middle pin of the encoder to ground.
* Connect one of the outer pins of the encoder to PA0 on the STM32F4.
* Connect the other outer pin of the encoder to PA1 on the STM32F4.

You do not need to connect 5V from the STM32F4 to anything, since the
PA0/1 pins will provide the current for the switches in the encoder to
function, if you configure them with the internal pull-up resistors
turned on.

Then use the `Encoder` class like this:

    import pyb
    from encoder import Encoder

    e = Encoder('A0', 'A1', pyb.Pin.PULL_UP)
    lastpos = e.position

    while True:
        if lastpos != e.position:
            lastpos = e.position
            print(lastpos)
        pyb.delay(100)


[pyboard]: http://docs.micropython.org/en/latest/pyboard/quickref.html
[blog post]: https://www.circuitsathome.com/mcu/reading-rotary-encoder-on-arduino