#!/usr/bin/python

#
# Author : David Sand
# Date   : 16/01/2019
#
#
# --------------------------------------

# Reading rate ≃ 20 ms

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
    def __init__(self, rm_lenght=50):
        super().__init__()

        self.bus = smbus.SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1

        # Rev 1 Pi uses bus 0

        self.temperature = 0
        self.pressure = 0
        self.humidity = 0
        self.hight = 0
        self.chip_id = 0
        self.chip_version = 0

        # Filter
        # rm = running mean
        self.rm_lenght = rm_lenght
        self.rm_sum = 0
        self.rm_input_index = 0
        self.rm_result = [0 for _ in range(0, self.rm_lenght)]

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

    def readBME280All(self, addr=device):
        temperature = 0
        pressure = 0
        humidity = 0
        hight = 0

        # Register Addresses
        REG_DATA = 0xF7
        REG_CONTROL = 0xF4
        REG_CONFIG = 0xF5

        REG_CONTROL_HUM = 0xF2
        REG_HUM_MSB = 0xFD
        REG_HUM_LSB = 0xFE

        # Oversample setting - page 27
        OVERSAMPLE_TEMP = 2
        OVERSAMPLE_PRES = 2
        MODE = 1

        # Oversample setting for self.humidity register - page 26
        OVERSAMPLE_HUM = 2
        self.bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

        control = OVERSAMPLE_TEMP << 5 | OVERSAMPLE_PRES << 2 | MODE
        self.bus.write_byte_data(addr, REG_CONTROL, control)

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
        wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + (
            (2.3 * OVERSAMPLE_HUM) + 0.575)
        time.sleep(wait_time / 1000)  # Wait the required time

        # Read temperature/pressure/self.humidity
        data = self.bus.read_i2c_block_data(addr, REG_DATA, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        # Refine self.temperature
        var1 = ((((temp_raw >> 3) - (dig_T1 << 1))) * (dig_T2)) >> 11
        var2 = (((((temp_raw >> 4) - (dig_T1)) *
                  ((temp_raw >> 4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
        t_fine = var1 + var2
        temperature = float(((t_fine * 5) + 128) >> 8)
        temperature = temperature/100.0

        # Refine self.pressure and adjust for self.temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_P6 / 32768.0
        var2 = var2 + var1 * dig_P5 * 2.0
        var2 = var2 / 4.0 + dig_P4 * 65536.0
        var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_P1
        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - pres_raw
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = dig_P9 * pressure * pressure / 2147483648.0
            var2 = pressure * dig_P8 / 32768.0
            pressure = pressure + (var1 + var2 + dig_P7) / 16.0

        # Refine self.humidity
        humidity = t_fine - 76800.0
        humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (
            1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
        humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
        if humidity > 100:
            humidity = 100
        elif humidity < 0:
            humidity = 0

        hight = ((101325/(pressure))**(1/5.257)-1) * (temperature + 273.15) / 0.0065

        return temperature, pressure, humidity, hight

    def get_data(self):
        self.temperature, self.pressure, self.humidity, self.hight = self.readBME280All()

    def show_data(self):
        self.get_data()

        print("BME280")
        print("----------------")

        print("Temperature : ", self.temperature, "C")
        print("Pressure : ", self.pressure, "Pa")
        print("Humidity : ", self.humidity, "%")
        print("Hight : ", self.hight, "m")

    def data_pack(self):
        self.get_data()
        data = [round(self.temperature, 1), round(self.pressure, 1), round(self.hight, 1)]
        return data

    def running_mean(self, data):
        self.rm_sum -= self.rm_result[self.rm_input_index]
        self.rm_result[self.rm_input_index] = data
        self.rm_sum += self.rm_result[self.rm_input_index]
        self.rm_input_index = (self.rm_input_index + 1) % self.rm_lenght

        # print("result", self.rm_result)
        # print("input_index", self.rm_input_index)
        # print("sum", self.rm_sum)

        return self.rm_sum/self.rm_lenght
