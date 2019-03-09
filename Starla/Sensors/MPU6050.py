#!/usr/bin/python
import smbus
import math
import sys

sys.path.append("/home/pi/Starla")
from Sensors.Sensor import Sensor

# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

bus = smbus.SMBus(1)  # bus = smbus.SMBus(0)
address = 0x68  # via i2cdetect

# Ativacao
bus.write_byte_data(address, power_mgmt_1, 0)


class MPU6050(Sensor):
    def __init__(self):
        super().__init__()
        
        self.acelerometer = self.Acelerometer()
        self.gyroscope = self.Gyroscope()

    class Acelerometer:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.z = 0
            self.x_scaled = 0
            self.y_scaled = 0
            self.z_scaled = 0

        def scale(self, a):
            return a / 16384.0

    class Gyroscope:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.z = 0

        def scale(self, a):
            return a / 131

    def read_byte(self, reg):
        return bus.read_byte_data(address, reg)

    def read_word(self, reg):
        h = bus.read_byte_data(address, reg)
        l = bus.read_byte_data(address, reg + 1)
        value = (h << 8) + l
        return value

    def read_word_2c(self, reg):
        val = self.read_word(reg)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def dist(self, a, b):
        return math.sqrt((a * a) + (b * b))

    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    def get_data(self):
        self.gyroscope.x = self.read_word_2c(0x43)
        self.gyroscope.y = self.read_word_2c(0x45)
        self.gyroscope.z = self.read_word_2c(0x47)

        self.gyroscope.x_scaled = self.gyroscope.scale(self.gyroscope.x)
        self.gyroscope.y_scaled = self.gyroscope.scale(self.gyroscope.y)
        self.gyroscope.z_scaled = self.gyroscope.scale(self.gyroscope.z)

        self.acelerometer.x = self.read_word_2c(0x3b)
        self.acelerometer.y = self.read_word_2c(0x3d)
        self.acelerometer.z = self.read_word_2c(0x3f)

        self.acelerometer.x_scaled = self.acelerometer.scale(self.acelerometer.x)
        self.acelerometer.y_scaled = self.acelerometer.scale(self.acelerometer.y)
        self.acelerometer.z_scaled = self.acelerometer.scale(self.acelerometer.z)

        self.xAngle = self.get_x_rotation(self.acelerometer.x_scaled, self.acelerometer.y_scaled, self.acelerometer.z_scaled)
        self.yAngle = self.get_y_rotation(self.acelerometer.x_scaled, self.acelerometer.y_scaled, self.acelerometer.z_scaled)
        self.zAngle = 0     # No magnetometer data

    def show_data(self):

        self.get_data()

        print("-------------")
        print("Gyroscope")
        print("-------------")

        print("Gyroscope_x: ", self.gyroscope.x_scaled)
        print("Gyroscope_y: ", self.gyroscope.y_scaled)
        print("Gyroscope_z: ", self.gyroscope.z_scaled)

        print("-------------")
        print("Acelerometer")
        print("-------------")

        print("Acelerometer_x: ", self.acelerometer.x_scaled)
        print("Acelerometer_y: ", self.acelerometer.y_scaled)
        print("Acelerometer_z: ", self.acelerometer.z_scaled)

        print("-------------")
        print("Whole Sensor")
        print("-------------")

        print("X Rotation: ", self.xAngle)
        print("Y Rotation: ", self.yAngle)

    def running_mean(self, data, N):
        sum = 0
        result = [0 for x in data]

        for i in range(0, N):
            sum = sum + data[i]
            result[i] = sum / (i + 1)

        for i in range(N, len(data)):
            sum = sum - data[i - N] + data[i]
            result[i] = sum / N

        return result

    def data_pack(self):
        self.get_data()
        return [round(self.xAngle, 1), round(self.yAngle, 1), round(self.zAngle, 1)]
