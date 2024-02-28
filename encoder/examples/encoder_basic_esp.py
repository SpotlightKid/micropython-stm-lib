"""Read encoder connected to an ESP8266 board and print position value.

Also demonstrates handling encoders, which switch several times per "click"
(detent), and acceleration, i.e. the encoder value increases more the faster
it is turned.

"""

from time import sleep_ms
from encoder import Encoder


def main():
    enc = Encoder(4, 5, max_val=999, clicks=4, accel=3)  # CLK = D2, DT = D1

    while True:
        # poll() returns value only if it has changed since last call
        if (val := enc.poll()) is not None:
            print(val)

        sleep_ms(50)


if __name__ == '__main__':
    main()
