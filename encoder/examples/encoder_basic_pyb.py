"""Read encoder connectd to a Pyboard and print position value."""

from time import sleep_ms
from pyb_encoder import Encoder


def main():
    enc = Encoder('A0', 'A1')

    while True:
        # poll() returns value only if it has changed since last call
        if (val := enc.poll()) is not None:
            print(val)

        sleep_ms(50)


if __name__ == '__main__':
    main()
