#
# spiflash.py
#
# Adapted from https://github.com/manitou48/pyboard
#
# SPI flash http://www.adafruit.com/product/1564
# SPI 1 42mhz max   SPI 2  21 mhz max
# SPI1 X5-X8 CS CLK MISO MOSI   3.3v grnd

__all__ = ('SPIFLash',)

from micropython import const


CMD_JEDEC_ID = const(0x9F)
CMD_READ_STATUS = const(0x05)    # Read status register
CMD_READ = const(0x03)           # Read @ low speed
CMD_READ_HI_SPEED = const(0x0B)  # Read @ high speed
CMD_WRITE_ENABLE = const(0x06)   # Write enable
CMD_PROGRAM_PAGE = const(0x02)   # Write page
CMD_ERASE_4K = const(0x20)
CMD_ERASE_32K = const(0x52)
CMD_ERASE_64K = const(0xD8)
CMD_ERASE_CHIP = const(0xC7)
CMD_READ_UID = const(0x4B)
PAGE_SIZE = const(256)
COMMANDS = {
    '4k': CMD_ERASE_4K,
    '32k': CMD_ERASE_32K,
    '64k': CMD_ERASE_64K
}


class SPIFlash:
    def __init__(self, spi, cs):
        self._spi = spi
        self._cs = cs
        self._cs.high()
        self._buf = bytearray([0])

    def _write(self, val):
        if isinstance(val, int):
            self._buf[0] = val
            self._spi.write(self._buf)
        else:
            self._spi.write(val)

    def read_block(self, addr, buf):
        self._cs.low()
        self._write(CMD_READ)
        self._write(addr >> 16)
        self._write(addr >> 8)
        self._write(addr)
        self._spi.readinto(buf)
        self._cs.high()

    def getid(self):
        self._cs.low()
        self._write(CMD_JEDEC_ID)  # id
        res = self._spi.read(3)
        self._cs.high()
        return res

    def wait(self):
        while True:
            self._cs.low()
            self._write(CMD_READ_STATUS)
            r = self._spi.read(1)[0]
            self._cs.high()

            if r == 0:
                return

    def write_block(self, addr, buf):
        # Write in 256-byte chunks
        # XXX: Should check that write doesn't go past end of flash ...
        length = len(buf)
        pos = 0

        while pos < length:
            size = min(length - pos, PAGE_SIZE)
            self._cs.low()
            self._write(CMD_WRITE_ENABLE)
            self._cs.high()

            self._cs.low()
            self._write(CMD_PROGRAM_PAGE)
            self._write(addr >> 16)
            self._write(addr >> 8)
            self._write(addr)
            self._write(buf[pos:pos + size])
            self._cs.high()
            self.wait()

            addr += size
            pos += size

    def erase(self, addr, cmd):
        self._cs.low()
        self._write(CMD_WRITE_ENABLE)
        self._cs.high()

        self._cs.low()
        self._write(COMMANDS[cmd])
        self._write(addr >> 16)
        self._write(addr >> 8)
        self._write(addr)
        self._cs.high()
        self.wait()

    def erase_chip(self):
        self._cs.low()
        self._write(CMD_WRITE_ENABLE)
        self._cs.high()

        self._cs.low()
        self._write(CMD_ERASE_CHIP)
        self._cs.high()
        self.wait()
