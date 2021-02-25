#!/usr/bin/python3

import spidev
import smbus
import adpi
import sys
from time import sleep

RAW_OFFSET = (1 << 23)
RAW_SCALE = (
    0.000596040,
    0.000298020,
    0.000149010,
    0.000074500,
    0.000037250,
    0.000018620,
    0.000009310,
    0.000004650,
)
TEMP_VREF = 1.17


def v2k(rate, val):
    for k, v in rate.items():
        if v == val:
            return k


def single_conversion(dev, ch):
    c = dev.adc.channel[ch]
    g, _ = dev.read_configuration()
    dev.write_configuration(g, c)
    _, r = dev.read_mode()
    dev.write_mode(dev.adc.mode['single'], r)
    rate = v2k(dev.adc.rate, r)

    while True:
        sleep(2 * 1.0 / float(rate))
        if not dev.read_status() & 0x80:
            break

    raw = dev.read_data()
    return raw, g


def get_voltage(dev, ch):
    raw, g = single_conversion(dev, ch)
    vol = RAW_SCALE[g] * (raw - RAW_OFFSET)
    return "  Ch {} : {:.1f}".format(ch,vol)


if __name__ == "__main__":
    spibus = 0
    spics = 0
    eeprombus = 1
    eepromaddr = 0x57
    gpiobus = 1
    gpioaddr = 0x27
    spi = spidev.SpiDev()
    i2c = smbus.SMBus(eeprombus)
    while(1):
        try:
            spi.open(spibus, spics)
            spi.mode = 0b11
            spi.max_speed_hz = 1000000
            ad = adpi.ADPiPro(spi, i2c, eepromaddr, gpioaddr)
            print("\r"+get_voltage(ad, "1")+get_voltage(ad, "2")+get_voltage(ad, "3")+get_voltage(ad, "4"), end='')
            # print(get_voltage(ad, "2"))
            # print(get_voltage(ad, "3"))
            # print(get_voltage(ad, "4"))
            sleep(0.2)

        except (IndexError, ValueError):
            sys.exit(2)
        finally:
            spi.close()