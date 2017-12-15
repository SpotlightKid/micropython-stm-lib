import gc
import ubinascii

from pyb import micros, Pin, SPI
from spiflash import SPIFlash


def test():
    print("SPI flash")
    cs = Pin('PB0', Pin.OUT_PP)
    spi = SPI(3, SPI.MASTER, baudrate=42000000, polarity=0, phase=0)
    flash = SPIFlash(spi, cs)

    print("Getting chip ID...")
    flash.wait()
    id_ = flash.getid()
    print("ID:", ubinascii.hexlify(id_))

    print("Reading block (32b) from address 0...")
    buf = bytearray(32)
    flash.read_block(0, buf)
    print(ubinascii.hexlify(buf))

    addr = 12 * 600 + 8
    print("Reading block (32b) from address {}...".format(addr))
    flash.read_block(addr, buf)
    print(ubinascii.hexlify(buf))

    addr = 524288
    print("Erasing 4k block at address {}...".format(addr))
    t1 = micros()
    flash.erase(addr, '4k')
    # flash.erase(addr, '32k')
    # flash.erase(addr, '64k')
    # flash.erase_chip()
    t = micros() - t1
    print("erase {} us".format(t))

    print("Writing blocks (256b) at address {}...".format(addr))
    buf = bytearray(range(256))
    t1 = micros()
    flash.write_block(addr, buf)
    t = micros() - t1
    mbs = len(buf) * 8. / t
    print("write({}) {} us, {} mbs".format(len(buf), t, mbs))

    print("Verifying write...")
    v = bytearray(256)
    flash.read_block(addr, v)
    if (v == buf):
        print("write/read ok")
    else:
        print("write/read FAILed")

    print("Timing 32k read from address 0...")
    gc.collect()
    buf = bytearray(32 * 1024)
    t1 = micros()
    flash.read_block(0, buf)
    t = micros() - t1
    mbs = len(buf) * 8. / t
    print("read({}) {} us, {} mbs".format(len(buf), t, mbs))


if __name__ == 'main':
    test()
