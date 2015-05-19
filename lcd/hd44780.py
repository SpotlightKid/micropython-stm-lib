# -*- coding: utf-8 -*-
"""HD44780 display controller library for MicroPython_

Based on:

* `micropython-lcd <http://github.com/wjdp/micropython-lcd>`_
  by Will Pimblett
* various AVR libraries for HD44780-based displays

.. _micropython: http://micropython.org

"""

import pyb

try:
    const
except NameError:
    def const(x):
        return x

HIGH = 1
LOW = 0

# Timing constants
E_PULSE = const(1)
E_DELAY = const(50)

# Pin names, don't change
PIN_NAMES = ('RS', 'EN', 'D4', 'D5', 'D6', 'D7')
# Pin mode, push-pull control
PIN_MODE = pyb.Pin.OUT_PP

# Command / character mode
LCD_CHR = HIGH
LCD_CMD = LOW

# LCD commands
LCD_CLEARDISPLAY = const(0x01)
LCD_RETURNHOME = const(0x02)
LCD_ENTRYMODESET = const(0x04)
LCD_DISPLAYCONTROL = const(0x08)
LCD_CURSORSHIFT = const(0x10)
LCD_FUNCTIONSET = const(0x20)
LCD_SETCGRAMADDR = const(0x40)
LCD_SETDDRAMADDR = const(0x80)

# flags for display entry mode
LCD_ENTRYRIGHT = const(0x00)
LCD_ENTRYLEFT = const(0x02)
LCD_ENTRYSHIFTINCREMENT = const(0x01)
LCD_ENTRYSHIFTDECREMENT = const(0x00)

# flags for display on/off control
LCD_DISPLAYON = const(0x04)
LCD_DISPLAYOFF = const(0x00)
LCD_CURSORON = const(0x02)
LCD_CURSOROFF = const(0x00)
LCD_BLINKON = const(0x01)
LCD_BLINKOFF = const(0x00)

# flags for display/cursor shift
LCD_DISPLAYMOVE = const(0x08)
LCD_CURSORMOVE = const(0x00)
LCD_MOVERIGHT = const(0x04)
LCD_MOVELEFT = const(0x00)

# flags for function set
LCD_8BITMODE = const(0x10)
LCD_4BITMODE = const(0x00)
LCD_2LINE = const(0x08)
LCD_1LINE = const(0x00)
LCD_5x10DOTS = const(0x04)
LCD_5x8DOTS = const(0x00)


class HD44780:
    """Interface to a HD44780 LCD controller in 4-bit mode."""

    _default_pins = ('Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Y6')
    row_offsets = (0x00, 0x40, 0x14, 0x54)

    def __init__(self, width=16, lines=2, pins=None, init=True):
        """Initialize instance and dictionary of output pin objects."""
        # Initialize dict of pin objects
        self.pins = {name: pyb.Pin(pin, PIN_MODE) for name, pin in
                     zip(PIN_NAMES, pins if pins else self._default_pins)}
        # Maximum characters per line
        self.width = width
        # Number of display rows
        self.lines = lines
        # State of display on/off, underscore & blinking cursor control
        self._displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        # State of text flow direction and auto-scrolling
        self._displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT

        if init:
            self.init()

    def init(self):
        """Initialize the display.

        When the display powers up, it is configured as follows:

        1. Display clear
        2. Function set:
            DL = 1 --> 8-bit interface data
            N =  0 --> 1-line display
            F =  0 --> 5x8 dot character font
        3. Display on/off control:
            D = 0 --> Display off
            C = 0 --> Cursor off
            B = 0 --> Blinking off
        4. Entry mode set:
            I/D = 1 --> Increment by 1
            S =   0 --> No shift

        """
        self._usleep(50000)

        # Pull RS low to begin commands
        self._set_pin('RS', LOW)
        self._set_pin('EN', LOW)

        # Put the LCD into 4 bit or 8 bit mode.
        # This is according to the hitachi HD44780 datasheet figure 24, p. 46
        # We start in 8bit mode, try to set 4 bit mode.
        self._send_nibble(0x03)
        self._usleep(40)

        # Second try
        self._send_nibble(0x03)
        self._usleep(20)

        # Third go!
        self._send_nibble(0x03)
        self._usleep(20)

        # Finally, set to 4-bit interface
        self._send_nibble(0x02)

        # Finally, set # lines, font size, etc.
        display_functions = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS

        if self.lines > 1:
            display_functions |= LCD_2LINE

        self.command(LCD_FUNCTIONSET | display_functions)

        # Turn the display on with no cursor or blinking default
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

        # Clear the display
        self.clear()

        # Set the entry mode; initialize to default text direction
        # (for romanic languages)
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def clear(self):
        """Clear the display."""
        self.command(LCD_CLEARDISPLAY)
        self._usleep(2000)

    def home(self):
        self.command(LCD_RETURNHOME)
        self._usleep(2000)

    def display(self, on=True):
        """Turn the display on or off."""
        if on:
            self._displaycontrol |= LCD_DISPLAYON
        else:
            self._displaycontrol &= ~LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def cursor(self, on=True):
        """Turn the underscore cursor on or off."""
        if on:
            self._displaycontrol |= LCD_CURSORON
        else:
            self._displaycontrol &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def blink(self, on=True):
        """Turn the blinking cursor on or off."""
        if on:
            self._displaycontrol |= LCD_BLINKON
        else:
            self._displaycontrol &= ~LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def scroll(self, direction=LCD_MOVERIGHT):
        """Scroll the display without changing the RAM."""
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | direction)

    def direction(self, direction=LCD_ENTRYLEFT):
        """Set text flow direction to left-to-right or right-to-left."""
        if direction == LCD_ENTRYLEFT:
            self._displaymode |= LCD_ENTRYLEFT
        else:
            self._displaymode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def autoscroll(self, on=True):
        """Turn autoscrolling on or off.

        When autoscrolling is on, when a character is written, the existing
        characters to the right of it (or left, depending on the text flow
        direction set with the ``direction()`` method), are scrolled one
        position to the right reps. left, to make space for it.

        """
        if on:
            self._displaymode |= LCD_ENTRYSHIFTINCREMENT
        else:
            self._displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def set_cursor(self, col, row=0):
        """Set the cursor the given column and row (default 0)."""
        self.command(LCD_SETDDRAMADDR | col + self.row_offsets[row])

    def send_byte(self, byte, mode=LCD_CHR):
        """Send a byte to the data pins.

        byte = data
        mode = LCD_CMD  for command
               LCD_CHAR for character

        """
        if isinstance(byte, bytes):
            byte = byte[0]
        elif isinstance(byte, str):
            byte = ord(byte[0])

        self._set_pin('RS', mode)
        self._send_nibble(byte >> 4)
        self._send_nibble(byte)

    def command(self, command):
        self.send_byte(command, mode=LCD_CMD)

    def write(self, message, col=None, row=None):
        """Write message to given row."""
        if col is not None or row is not None:
            self.set_cursor(col or 0, row or 0)

        for c in message:
            self.send_byte(c)

    def create_char(self, location, charmap):
        """Create a custom character in given memory location.

        Allows us to fill the first 8 CGRAM locations with custom characters.
        There are 8 locations, 0-7

        """
        self.command(LCD_SETCGRAMADDR | ((location & 0x7) << 3))

        for c in charmap:
            self.send_byte(c)

    # internal helper methods
    def _pulse_enable(self):
        """Pulse the EN pin, by setting it low, then high, then low again."""
        self._set_pin('EN', LOW)
        self._usleep(E_PULSE)
        self._set_pin('EN', HIGH)
        self._usleep(E_PULSE)
        self._set_pin('EN', LOW)
        self._usleep(E_DELAY)

    def _usleep(self, us):
        """Delay by (sleep) us microseconds."""
        # Wrapped as a method for portability
        pyb.udelay(us)

    def _set_pin(self, pin, state):
        """Set output pin high or low."""
        # Wrapped as a method for portability
        if state:
            self.pins[pin].high()
        else:
            self.pins[pin].low()

    def _send_nibble(self, nibble):
        """Send a nibble (4 bits) by setting data pins D4-7 and pulsing EN."""
        self._set_pin('D4', nibble >> 0 & 1)
        self._set_pin('D5', nibble >> 1 & 1)
        self._set_pin('D6', nibble >> 2 & 1)
        self._set_pin('D7', nibble >> 3 & 1)
        self._pulse_enable()
