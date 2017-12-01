# Connect in station mode. Use saved parameters if possible to save flash wear

import json
import network
import time


# Configuraion defaults
# Try to connect using the default network config saved in flash
USE_DEFAULT = True
# Give up trying to connect with default network config after this many seconds
# A value of -1 means re-try forever until connected
TIMEOUT_DEFAULT_CONFIG = 5
# Give up trying to connect with custom network config after this many seconds
# A value of -1 means re-try forever until connected
TIMEOUT = 5
# Enable wifi. If False, interface is deactivated
ENABLED = True


def connect(configfile):
    """Try to connect to WiFi network.

    Reads network configuration (SSID, password, etc.) from JSON
    file with specified with `configfile` argument.

    Example configuration file contents:

        {
            "ssid": "My WLAN",
            "password": "XXXXXXXX",
            "use_default": 1,
            "timeout_default_config": 3,
            "timeout": 8
        }

    """
    try:
        with open(configfile) as fp:
            config = json.loads(fp.read())
    except (IOError, OSError):
        config = {}

    sta_if = network.WLAN(network.STA_IF)

    if not config.get('enabled', ENABLED):
        sta_if.active(False)
        return False

    if config.get('use_default', USE_DEFAULT):
        timeout = config.get('timeout_default_config',
                             TIMEOUT_DEFAULT_CONFIG)

        while timeout != 0 and not sta_if.isconnected():
            time.sleep(1)
            timeout = max(-1, timeout - 1)

    # If can't use default, use WLAN info specified in config
    if not sta_if.isconnected() and config.get('ssid'):
        sta_if.active(True)
        sta_if.connect(config['ssid'], config.get('password'), bssid=config.get('bssid'))
        timeout = config.get('timeout', TIMEOUT)

        while timeout != 0 and not sta_if.isconnected():
            time.sleep(1)
            timeout = max(-1, timeout - 1)

    return sta_if.isconnected()
