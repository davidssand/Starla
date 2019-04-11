#!/usr/bin/python

#
# Author : David Sand
# Date   : 16/01/2019
#
#
# --------------------------------------

import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
import sys

sys.path.append("/home/pi/Starla")
from Sensors.Sensor import Sensor

device = 0x76  # Default device I2C address

class BME280(Sensor):
    def __init__(self):
        super().__init__()

        self.bus = smbus.SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1

        # Rev 1 Pi uses bus 0

        self.temperature = 0
        self.pressure = 0
        self.humidity = 0
        self.hight = 0
        self.chip_id = 0
        self.chip_version = 0

        # Register Addresses
        self.REG_DATA = 0xF7
        self.REG_CONTROL = 0xF4
        self.REG_CONFIG = 0xF5

        self.REG_CONTROL_HUM = 0xF2
        self.REG_HUM_MSB = 0xFD
        self.REG_HUM_.LSB = 0xFE

        # Oversample setting - page 27
        self.OVERSAMPLE_TEMP = 2
        self.OVERSAMPLE_PRES = 2
        self.MODE = 1

        self.OVERSAMPLE_HUM  = 2

    def getShort(self, data, index):
        # return two bytes from data as a signed 16-bit value
        return c_short((data[index + 1] << 8) + data[index]).value

    def getUShort(self, data, index):
        # return two bytes from data as an unsigned 16-bit value
        return (data[index + 1] << 8) + data[index]

    def getChar(self, data, index):
        # return one byte from data as a signed char
        result = data[index]
        if result > 127:
            result -= 256
        return result

    def getUChar(self, data, index):
        # return one byte from data as an unsigned char
        result = data[index] & 0xFF
        return result

    def readBME280ID(self, addr=device):
        # Chip ID Register Address
        REG_ID = 0xD0
        (chip_id, chip_version) = self.bus.read_i2c_block_data(addr, REG_ID, 2)
        return (chip_id, chip_version)

    def get_data(self, addr=device):
        # Oversample setting for self.humidity register - page 26
        self.bus.write_byte_data(addr, self.REG_CONTROL_HUM, self.OVERSAMPLE_HUM )

        control = self.OVERSAMPLE_TEMP << 5 | self.OVERSAMPLE_PRES << 2 | self.MODE
        self.bus.write_byte_data(addr, self.REG_CONTROL, control)

        # Read blocks of calibration data from EEPROM
        # See Page 22 data sheet
        cal1 = self.bus.read_i2c_block_data(addr, 0x88, 24)
        cal2 = self.bus.read_i2c_block_data(addr, 0xA1, 1)
        cal3 = self.bus.read_i2c_block_data(addr, 0xE1, 7)

        # Convert byte data to word values
        dig_T1 = self.getUShort(cal1, 0)
        dig_T2 = self.getShort(cal1, 2)
        dig_T3 = self.getShort(cal1, 4)

        dig_P1 = self.getUShort(cal1, 6)
        dig_P2 = self.getShort(cal1, 8)
        dig_P3 = self.getShort(cal1, 10)
        dig_P4 = self.getShort(cal1, 12)
        dig_P5 = self.getShort(cal1, 14)
        dig_P6 = self.getShort(cal1, 16)
        dig_P7 = self.getShort(cal1, 18)
        dig_P8 = self.getShort(cal1, 20)
        dig_P9 = self.getShort(cal1, 22)

        dig_H1 = self.getUChar(cal2, 0)
        dig_H2 = self.getShort(cal3, 0)
        dig_H3 = self.getUChar(cal3, 2)

        dig_H4 = self.getChar(cal3, 3)
        dig_H4 = (dig_H4 << 24) >> 20
        dig_H4 = dig_H4 | (self.getChar(cal3, 4) & 0x0F)

        dig_H5 = self.getChar(cal3, 5)
        dig_H5 = (dig_H5 << 24) >> 20
        dig_H5 = dig_H5 | (self.getUChar(cal3, 4) >> 4 & 0x0F)

        dig_H6 = self.getChar(cal3, 6)

        # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
        wait_time = 1.25 + (2.3 * self.OVERSAMPLE_TEMP) + ((2.3 * self.OVERSAMPLE_PRES) + 0.575) + (
                    (2.3 * self.OVERSAMPLE_HUM ) + 0.575)
        time.sleep(wait_time / 1000)  # Wait the required time

        # Read temperature/pressure/humidity
        data = self.bus.read_i2c_block_data(addr, self.REG_DATA, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        # Refine temperature
        var1 = ((((temp_raw >> 3) - (dig_T1 << 1))) * (dig_T2)) >> 11
        var2 = (((((temp_raw >> 4) - (dig_T1)) * ((temp_raw >> 4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
        t_fine = var1 + var2
        self.temperature = float(((t_fine * 5) + 128) >> 8)
        self.temperature = self.temperature/100.0

        # Refine pressure and adjust for self.temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_P6 / 32768.0
        var2 = var2 + var1 * dig_P5 * 2.0
        var2 = var2 / 4.0 + dig_P4 * 65536.0
        var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_P1
        if var1 == 0:
            self.pressure = 0
        else:
            self.pressure = 1048576.0 - pres_raw
            self.pressure = ((self.pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = dig_P9 * self.pressure * self.pressure / 2147483648.0
            var2 = self.pressure * dig_P8 / 32768.0
            self.pressure = self.pressure + (var1 + var2 + dig_P7) / 16.0
        self.pressure = self.pressure/100.0

        # Refine humidity
        self.humidity = t_fine - 76800.0
        self.humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * self.humidity)) * (dig_H2 / 65536.0 * (
                    1.0 + dig_H6 / 67108864.0 * self.humidity * (1.0 + dig_H3 / 67108864.0 * self.humidity)))
        self.humidity = self.humidity * (1.0 - dig_H1 * self.humidity / 524288.0)
        if self.humidity > 100:
            self.humidity = 100
        elif self.humidity < 0:
            self.humidity = 0

        # Refine high        
        self.hight = ((1013.25/(self.pressure/100))**(1/5.257)-1)*(self.temperature/100+273.15)/0.0065

    def show_data(self):
        self.get_data()

        print("BME280")
        print("----------------")

        print("self.temperature : ", self.temperature, "C")
        print("self.pressure : ", self.pressure, "hPa")
        print("self.humidity : ", self.humidity, "%")
        print("self.hight : ", self.hight, "m\n")
    
    def data_pack(self):
        self.get_data()
        data = [round(self.temperature, 1), round(self.pressure, 1), round(self.hight, 1)]
        return data

