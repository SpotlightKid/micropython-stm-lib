"""Example of handling encoder updates in an asyncio-based application."""

import asyncio
from machine import Pin
from time import sleep_ms

from encoder import Encoder


UPDATE_INTERVAL = const(50)
ENC_PIN_CLK = const(4)
ENC_PIN_DT = const(5)


async def handle_encoder_update(q, evt):
    while True:
        await evt.wait()
        value = q.pop(0)
        evt.clear()
        print("New encoder value:",  value)


async def check_encoder(enc, q, evt):
    while True:
        if (value := enc.poll()) is not None:
            q.append(value)
            evt.set()

        await asyncio.sleep_ms(UPDATE_INTERVAL)


async def main():
    # Encoder dial handling
    evt = asyncio.Event()
    queue = []
    enc = Encoder(pin_clk=ENC_PIN_CLK, pin_dt=ENC_PIN_DT, clicks=4, accel=7)
    task1 = asyncio.create_task(handle_encoder_update(queue, evt))
    task2 = asyncio.create_task(check_encoder(enc, queue, evt))

    print('Ready.')

    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state
