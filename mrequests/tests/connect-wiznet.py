"""Sets up network on MicroPython board with Wiznet 5500 ethernet adapter attached via SPI.

This uses the netconfig_ module from my ``micropython-stm-lib``.

To compile the MicroPython ``stm32`` port with support for the Wiznet 5500 adapter,
add the following to ``mpconfigboard.mk`` in your board definition::

    MICROPY_PY_WIZNET5K = 5500
    MICROPY_PY_LWIP ?= 1
    MICROPY_PY_USSL ?= 1
    MICROPY_SSL_MBEDTLS ?= 1

and re-compile & upload the firmware::

   cd mpy-cross
   make
   cd ../ports/stm32
   make submodules
   make BOARD=MYBOARD
   # do whatever it takes connect your board in DFU mode
   make BOARD=MYBOARD deploy


.. _netconfig: https://github.com/SpotlightKid/micropython-stm-lib/tree/master/netconfig

"""

from netconfig import connect
nic = connect('paddyland-wiznet.json', True)
print(nic.ifconfig())
