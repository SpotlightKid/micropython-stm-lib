#
# dht11_logger.py - periodically reads temperature and humidity from a DHT11
#     sensor and logs it as JSON data to a Redis server or a btree database
#     file in the Flash storage.
#

import btree
import dht
import json
import machine
import network
import ntptime
import time

from micropython import const
from picoredis import Redis


LOGGING_INTERVAL = 300  # in seconds
REDIS_HOST = '192.168.1.111'
REDIS_PORT = 6379
REDIS_PASSWORD = 'XXXXXXXX'
# a machine ID of the form -XX-XX-XX-XX wil be appended to this
REDIS_KEY_PREFIX = 'esp8266-dht11'
LOGGER_NAME = 'dht11-logger'
DATABASE_FILENAME = 'dht11-logger.db'
DT_ISOFORMAT = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}"
DATA_PIN = const(0)  # D1 on NodeMCU board


class Logger:
    def __init__(self, name, filename=None,
                 format="{timestamp}:{name}:{level}:{message}\n"):
        self.name = name
        self.format = format
        if filename:
            self.filename = filename
        else:
            self.filename = name + '.log'

    def log(self, message, level='info'):
        try:
            with open(self.filename, 'a') as fp:
                now = time.localtime()
                fp.write(
                    self.format.format(name=self.name, level=level,
                                       message=message.rstrip(),
                                       timestamp=DT_ISOFORMAT.format(*now)))
        except (OSError, IOError):
            pass


def write_to_db(dbname, key, data):
    try:
        fp = open(dbname, 'r+b')
    except OSError:
        fp = open(dbname, 'w+b')

    db = btree.open(fp)
    db[key] = data
    db.flush()
    db.close()
    fp.close()


def main():
    logger = Logger(LOGGER_NAME)
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    reset_cause = machine.reset_cause()
    data_pin = machine.Pin(DATA_PIN)
    dht11 = dht.DHT11(data_pin)
    nic = network.WLAN(network.STA_IF)
    machine_id = "-".join("{:02X}".format(c) for c in machine.unique_id())
    redis_key = REDIS_KEY_PREFIX + '-' + machine_id

    if reset_cause != machine.DEEPSLEEP_RESET:
        logger.log("Starting up DHT11 data logger.", level='info')

    if not nic.isconnected():
        nic.connect()
        # print("Waiting for connection...")
        while not nic.isconnected():
            time.sleep(0.2)

    ntptime.settime()
    if reset_cause != machine.DEEPSLEEP_RESET:
        ifconfig = nic.ifconfig()
        logger.log("Connected to network with address {}.".format(ifconfig[0]),
                   level='info')

    while True:
        now = time.localtime()
        start = time.time()
        dht11.measure()
        data = {
            'humidity': dht11.humidity(),
            'temperature': dht11.temperature(),
            'timestamp': DT_ISOFORMAT.format(*now)
        }
        json_data = json.dumps(data)

        res = 0
        if nic.isconnected():
            try:
                redis = Redis(REDIS_HOST, REDIS_PORT)
                if REDIS_PASSWORD:
                    redis.auth(REDIS_PASSWORD)
                # returns new length of list
                res = redis.lpush(redis_key, json_data)
            except Exception as exc:
                logger.log("Could not write data to Redis: {}".format(exc),
                           level='error')

            try:
                redis.close()
            except OSError:
                pass

        if res < 1:
            try:
                write_to_db(DATABASE_FILENAME, data['timestamp'], json_data)
            except Exception as exc:
                logger.log("Could not write data to database: {}".format(exc),
                           level='error')

        wakeup_time = max(1, round(LOGGING_INTERVAL - (time.time() - start))) * 1000
        rtc.alarm(rtc.ALARM0, wakeup_time)
        machine.deepsleep()
