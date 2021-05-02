"""Connect a MicroPython board to an IP network."""

import json
import network
import time

# Configuration defaults
# ----------------------
#
# Which interface to connect with ('wifi', 'lan', 'wiznet')
# Available interfaces depend on MicroPython board / firmware used
INTERFACE = "wifi"
# Enable network. If False, interface is deactivated
ENABLED = True
# Try to connect with the custom network config for this many seconds
# A value of -1 means re-try forever until connected
TIMEOUT = 5

# How to configure the IP network ('static' / 'dhcp')
IP_CONFIG = "dhcp"

# Static IP configuration (ignored if IP_CONFIG is 'dhcp')
IP_ADDRESS = "192.168.1.100"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.1.0"
DNS = "192.168.1.0"

# For WiFi
# Try to connect using the default network config saved in flash
# to reduce flash wear
USE_DEFAULT = True
# Try to connect with the saved default network config for this many seconds
# A value of -1 means re-try forever until connected
TIMEOUT_DEFAULT_CONFIG = 5

# For WIZNET5K interface
# Number of the SPI bus the Wiznet 5x00 chip/board is connected to
SPI_BUS = 1
# The board pin connected to the Wiznet's reset (RST) pin
PIN_RST = "A3"
# The board pin connected to the Wiznet's slave select (SS/SCS) pin
PIN_SS = "A4"


def connect(configfile):
    """Try to connect to an Ethernet or WiFi network.

    Reads the network configuration (interface, IP config, SSID, password,
    etc.) from the JSON file specified with the `configfile` argument.

    Returns the network interface object instance.

    Example configuration file contents:

        {
            "interface": "wifi"
            "ssid": "My WLAN",
            "password": "XXXXXXXX",
            "use_default": 1,
            "timeout_default_config": 3,
            "timeout": 8
        }

    or, for ethernet using the WIZNET5K driver with DHCP:

        {
            "interface": "wiznet",
            "ip_config": "dhcp"
            "spi_bus": 2,
            "pin_rst": "B11",
            "pin_ss": "B12",
            "timeout": 3,
        }

    or with static IP configuration:

        {
            "interface": "wiznet",
            "ip_config": "static"
            "spi_bus": 1,
            "pin_rst": "A3",
            "pin_ss": "A4",
            "ip_address": "192.168.1.100",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "dns": "192.168.1.1",
        }


    """
    try:
        with open(configfile) as fp:
            config = json.loads(fp.read())
        if not isinstance(config, dict):
            raise ValueError
    except (OSError, ValueError):
        config = {}

    interface = config.get("interface", INTERFACE).lower()
    print("Using '%s' interface." % interface)

    if interface == "wifi":
        net_if = network.WLAN(network.STA_IF)
    elif interface == "lan":
        net_if = network.LAN()
    elif interface == "wiznet":
        from machine import Pin, SPI

        pin_rst = config.get("pin_rst", PIN_RST)
        pin_ss = config.get("pin_ss", PIN_SS)
        spi_bus = int(config.get("spi_bus", SPI_BUS))
        net_if = network.WIZNET5K(SPI(spi_bus), Pin(pin_ss), Pin(pin_rst))

    if not config.get("enabled", ENABLED):
        net_if.active(False)
        print("Interface disabled.")
        return False
    else:
        print("Interface enabled.")
        net_if.active(True)

    if interface == "wifi" and config.get("use_default", USE_DEFAULT):
        print("Trying saved default WiFi configuration.")
        timeout = int(config.get("timeout_default_config", TIMEOUT_DEFAULT_CONFIG))

        while timeout != 0 and not net_if.isconnected():
            time.sleep(1)
            timeout = max(-1, timeout - 1)

    if not net_if.isconnected() and interface == "wifi" and "ssid" in config:
        # If we can't use default wifi config, use wifi from config
        print("Connecting to WiFi network '%s'..." % config["ssid"])
        net_if.connect(
            config["ssid"], config.get("password"), bssid=config.get("bssid")
        )
        timeout = int(config.get("timeout", TIMEOUT))

        while timeout != 0 and not net_if.isconnected():
            time.sleep(1)
            timeout = max(-1, timeout - 1)

    ip_config = config.get("ip_config", IP_CONFIG).lower()

    if not net_if.isconnected():
        if ip_config == "static":
            print("Setting static IP network configuration.")
            net_if.ifconfig(
                (
                    config.get("ip_address", IP_ADDRESS),
                    config.get("subnet_mask", SUBNET_MASK),
                    config.get("gateway", GATEWAY),
                    config.get("dns", DNS),
                )
            )
        else:
            print("Configuring IP network via DHCP...")
            net_if.ifconfig("dhcp")

    return net_if
