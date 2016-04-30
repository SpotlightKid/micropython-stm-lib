# -*- coding: utf-8 -*-
"""Driver for accelerometer on STM32F4-Discovery board.

Sets accelerometer range at +-2g.

Returns tuple containing (X, Y, Z) axis acceleration values in 'g' units
(9.8m/s^2).

See:

* STM32Cube_FW_F4_V1.1.0/Drivers/BSP/Components/lis302dl/lis302dl.h
* STM32Cube_FW_F4_V1.1.0/Drivers/BSP/Components/lis302dl/lis302dl.c
* STM32Cube_FW_F4_V1.1.0/Drivers/BSP/STM32F4-Discovery/stm32f4_discovery.c
* STM32Cube_FW_F4_V1.1.0/Drivers/BSP/STM32F4-Discovery/stm32f4_discovery.h
* STM32Cube_FW_F4_V1.1.0/Drivers/BSP/STM32F4-Discovery/stm32f4_discovery_accelerometer.c
* STM32Cube_FW_F4_V1.1.0/Drivers/BSP/STM32F4-Discovery/stm32f4_discovery_accelerometer.h
* STM32Cube_FW_F4_V1.1.0/Projects/STM32F4-Discovery/Demonstrations/Src/main.c

"""

from pyb import Pin, SPI


READWRITE_CMD = const(0x80)
MULTIPLEBYTE_CMD = const(0x40)
WHO_AM_I_ADDR = const(0x0f)
OUT_X_ADDR = const(0x29)
OUT_Y_ADDR = const(0x2b)
OUT_Z_ADDR = const(0x2d)
OUT_T_ADDR = const(0x0c)

LIS302DL_WHO_AM_I_VAL = const(0x3b)
LIS302DL_CTRL_REG1_ADDR = const(0x20)
# Configuration for 100Hz sampling rate, +-2g range
LIS302DL_CONF = const(0b01000111)

LIS3DSH_WHO_AM_I_VAL = const(0x3f)
LIS3DSH_CTRL_REG4_ADDR = const(0x20)
LIS3DSH_CTRL_REG5_ADDR = const(0x24)
# Configuration for 100Hz sampling rate, +-2g range
LIS3DSH_CTRL_REG4_CONF = const(0b01100111)
LIS3DSH_CTRL_REG5_CONF = const(0b00000000)


class STAccel:
    def __init__(self, cs='PE3', spi=1, debug=False):
        self._debug = debug
        self.cs_pin = Pin(cs, Pin.OUT_PP, Pin.PULL_NONE)
        self.cs_pin.high()
        self.spi = SPI(spi, SPI.MASTER, baudrate=328125, polarity=0, phase=1,
                       bits=8)

        self.read_id()
        # First SPI read always returns 255 --> discard and read ID again
        self.who_am_i = self.read_id()
        self.debug("Accel-ID: %s" % self.who_am_i)

        if self.who_am_i == LIS302DL_WHO_AM_I_VAL:
            self.write_bytes(LIS302DL_CTRL_REG1_ADDR, LIS302DL_CONF)
            self.sensitivity = 18
        elif self.who_am_i == LIS3DSH_WHO_AM_I_VAL:
            self.write_bytes(LIS3DSH_CTRL_REG4_ADDR, LIS3DSH_CTRL_REG4_CONF)
            self.write_bytes(LIS3DSH_CTRL_REG5_ADDR, LIS3DSH_CTRL_REG5_CONF)
            self.sensitivity = 0.06 * 256
        else:
            msg = 'LIS302DL or LIS3DSH accelerometer not present'

            if self._debug:
                self.debug(msg)
            else:
                raise IOError(msg)

    def debug(self, *msg):
        if self._debug:
            print(" ".join(str(m) for m in msg))

    def _convert_raw_to_g(self, x):
        if x & 0x80:
            x -= 256

        return x * self.sensitivity / 1000

    def read_bytes(self, addr, nbytes):
        self.cs_pin.low()

        if nbytes > 1:
            self.spi.send(addr | READWRITE_CMD | MULTIPLEBYTE_CMD)
        else:
            self.spi.send(addr | READWRITE_CMD)

        # read data, MSB first
        buf = self.spi.recv(nbytes)
        self.cs_pin.high()
        return buf

    def write_bytes(self, addr, buf):
        if not isinstance(buf, (int, bytes, bytearray)):
            buf = bytes(buf)

        if not isinstance(buf, int) and len(buf) > 1:
            addr |= MULTIPLEBYTE_CMD

        self.cs_pin.low()
        self.spi.send(addr)
        self.spi.send(buf)
        self.cs_pin.high()

    def read_id(self):
        return self.read_bytes(WHO_AM_I_ADDR, 1)[0]

    def x(self):
        return self._convert_raw_to_g(self.read_bytes(OUT_X_ADDR, 1)[0])

    def y(self):
        return self._convert_raw_to_g(self.read_bytes(OUT_Y_ADDR, 1)[0])

    def z(self):
        return self._convert_raw_to_g(self.read_bytes(OUT_Z_ADDR, 1)[0])

    def xyz(self):
        return (self.x(), self.y(), self.z())
