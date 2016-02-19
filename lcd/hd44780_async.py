from uasyncio.core import coroutine, sleep

from hd44780 import HD44780


class AsyncHD44780(HD44780):
    """Async interface to a HD44780 LCD controller in 4-bit mode."""

    @coroutine
    def _usleep(self, us):
        """Delay by (sleep) us microseconds."""
        yield from sleep(us / 1000)
