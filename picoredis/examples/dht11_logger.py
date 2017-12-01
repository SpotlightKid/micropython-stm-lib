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

from logger import Logger
from picoredis import Redis


LOGGING_INTERVAL = 300  # in seconds
REDIS_HOST = '192.168.1.111'
REDIS_PORT = 6379
REDIS_PASSWORD = None
# a machine ID of the form -XX-XX-XX-XX wil be appended to this
REDIS_KEY_PREFIX = 'esp8266-dht11'
LOGGER_NAME = 'dht11-logger'
DATABASE_NAME = 'dht11-logger.db'
DT_ISOFORMAT = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}"
DATA_PIN = const(0)  # D1 on NodeMCU board


def load_config(configfile):
    try:
        with open(configfile) as fp:
            return json.loads(fp.read())
    except OSError:
        return {}


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
    # Read configuration
    config = load_config('dht11-logger.json')
    logging_interval = config.get('logging_interval', LOGGING_INTERVAL)
    data_pin = machine.Pin(config.get('data_pin', DATA_PIN))
    machine_id = "-".join("{:02X}".format(c) for c in machine.unique_id())
    redis_key = (config.get('redis_key_prefix', REDIS_KEY_PREFIX) +
                 '-' + machine_id)

    # Create the objects we work with
    logger = Logger(config.get('logger_name', LOGGER_NAME))
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    reset_cause = machine.reset_cause()
    dht11 = dht.DHT11(data_pin)
    nic = network.WLAN(network.STA_IF)

    if reset_cause != machine.DEEPSLEEP_RESET:
        logger.log("Starting up DHT11 data logger.")

    # Wait for network to be up
    if not nic.isconnected():
        nic.connect()
        while not nic.isconnected():
            time.sleep(0.2)

    # And set the RTC
    ntptime.settime()

    if reset_cause != machine.DEEPSLEEP_RESET:
        ifconfig = nic.ifconfig()
        logger.log("Connected to network with address {}.".format(ifconfig[0]))

    # Now periodically log data and send it to Redis or write it to a local DB
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
                redis = Redis(config.get('redis_host', REDIS_HOST),
                              config.get('redis_port', REDIS_PORT))
                password = config.get('redis_password', REDIS_PASSWORD)

                if password:
                    redis.auth(password)

                # Returns new length of list
                res = redis.lpush(redis_key, json_data)
            except Exception as exc:
                logger.log("Could not write data to Redis: {}".format(exc),
                           level='error')

            try:
                redis.close()
            except (NameError, OSError):
                pass

        if res < 1:
            try:
                write_to_db(config.get('database_name', DATABASE_NAME),
                            data['timestamp'], json_data)
            except Exception as exc:
                logger.log("Could not write data to database: {}".format(exc),
                           level='error')

        # Go to sleep until the next logging cycle starts
        wakeup_time = max(1, round(logging_interval - (time.time() - start))) * 1000
        rtc.alarm(rtc.ALARM0, wakeup_time)
        machine.deepsleep()
