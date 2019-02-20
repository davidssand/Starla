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

    def readData(self):
        self.gyroscope.x = self.read_word_2c(0x43)
        self.gyroscope.y = self.read_word_2c(0x45)
        self.gyroscope.z = self.read_word_2c(0x47)

        self.acelerometer.x = self.read_word_2c(0x3b)
        self.acelerometer.y = self.read_word_2c(0x3d)
        self.acelerometer.z = self.read_word_2c(0x3f)

        self.acelerometer.x_scaled = self.acelerometer.scale(self.acelerometer.x)
        self.acelerometer.y_scaled = self.acelerometer.scale(self.acelerometer.y)
        self.acelerometer.z_scaled = self.acelerometer.scale(self.acelerometer.z)

    def showData(self):

        self.readData()

        print("Gyroscope")
        print("----------------")

        print("Gyroscope_xout: ", ("%5d" % self.gyroscope.x), " scaled: ", (self.gyroscope.x / 131))
        print("Gyroscope_yout: ", ("%5d" % self.gyroscope.y), " scaled: ", (self.gyroscope.y / 131))
        print("Gyroscope_zout: ", ("%5d" % self.gyroscope.z), " scaled: ", (self.gyroscope.z / 131))

        print("Acelerometer")
        print("----------------")

        print("Acelerometer_xout: ", ("%6d" % self.acelerometer.x), " scaled: ", self.acelerometer.x_scaled)
        print("Acelerometer_yout: ", ("%6d" % self.acelerometer.y), " scaled: ", self.acelerometer.y_scaled)
        print("Acelerometer_zout: ", ("%6d" % self.acelerometer.z), " scaled: ", self.acelerometer.z_scaled)

        print("X Rotation: ",
              self.get_x_rotation(self.acelerometer.x_scaled, self.acelerometer.y_scaled, self.acelerometer.z_scaled))
        print("Y Rotation: ",
              self.get_y_rotation(self.acelerometer.x_scaled, self.acelerometer.y_scaled, self.acelerometer.z_scaled))

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

    def dataPackage(self):
        self.readData()
        xAngle = self.get_x_rotation(self.acelerometer.x_scaled, self.acelerometer.y_scaled, self.acelerometer.z_scaled)
        yAngle = self.get_y_rotation(self.acelerometer.x_scaled, self.acelerometer.y_scaled, self.acelerometer.z_scaled)
        zAngle = 0
        return [round(xAngle, 1), round(yAngle, 1), round(zAngle, 1)]
