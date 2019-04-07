#!/usr/bin/python
import smbus
import math
import sys
import numpy as np

sys.path.append("/home/pi/Starla")
from Sensors.Sensor import Sensor


class MPU6050(Sensor):
    def __init__(self):
        super().__init__()

        # Register
        self.power_mgmt_1 = 0x6b
        self.power_mgmt_2 = 0x6c

        self.bus = smbus.SMBus(1)  # bus = smbus.SMBus(0)
        self.address = 0x68  # via i2cdetect

        # Ativacao
        self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)
        
        self.accelerometer = self.accelerometer()
        self.gyroscope = self.Gyroscope()

        self.angle = np.array([0, 0, 0])
        self.z_acceleration = 0

    class accelerometer:
        def __init__(self):
            self.raw = np.array([0, 0, 0])
            self.scaled = np.array([0, 0, 0])
            self.angle = np.array([0, 0, 0])

        def scale(self, a):
            return a / 16384.0  # Convert to G's

    class Gyroscope:
        def __init__(self):
            self.raw = np.array([0, 0, 0])
            self.scaled = np.array([0, 0, 0])
            self.angle = np.array([0, 0, 0])

        def scale(self, a):
            return a / 131  # Convert to degrees/second

    def read_byte(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_word(self, reg):
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg + 1)
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

    def get_raw_data(self):
        self.gyroscope.raw[0] = self.read_word_2c(0x43)
        self.gyroscope.raw[1] = self.read_word_2c(0x45)
        self.gyroscope.raw[2] = self.read_word_2c(0x47)
        self.accelerometer.raw[0] = self.read_word_2c(0x3b)
        self.accelerometer.raw[1] = self.read_word_2c(0x3d)
        self.accelerometer.raw[2] = self.read_word_2c(0x3f)
    
    def get_scaled_data(self):
        self.get_raw_data()
        self.gyroscope.scaled = -self.gyroscope.scale(self.gyroscope.raw)
        self.accelerometer.scaled = self.accelerometer.scale(self.accelerometer.raw)

    def get_rotation_rad(self, v):
        return [math.atan2(v[0], self.dist(v[1], v[2])), -math.atan2(v[1], self.dist(v[0], v[2])), math.atan2(v[2], self.dist(v[0], v[1]))]
    
    def get_rotation_deg(self, v):
        return -(np.degrees(self.get_rotation_rad(v)))
    
    def get_z_acceleration(self, v):
        return np.sum(np.absolute(v))

    # Complementary Filter
    def filtered_angle(self, sampling_rate, gyroscope_angle, accelerometer_angle):
        alpha = 1 / (1 + sampling_rate)
        return alpha * gyroscope_angle + (1 - alpha) * accelerometer_angle

    def get_data(self, sampling_rate):
        self.get_scaled_data()

        self.accelerometer.angle = self.get_rotation_deg(self.accelerometer.scaled)
        self.gyroscope.angle = self.angle + self.gyroscope.scaled * sampling_rate
        self.angle = self.filtered_angle(sampling_rate, self.gyroscope.angle, self.accelerometer.angle)     
        
        self.z_acceleration = self.get_z_acceleration(self.accelerometer.scaled)
        
    def show_data(self, sampling_rate):
        self.get_data(sampling_rate)

        print("-------------")
        print("Gyroscope")
        print("-------------")

        print("Gyroscope_angles: ", self.gyroscope.angle)

        print("-------------")
        print("Accelerometer")
        print("-------------")

        print("Accelerometer_acc: ", self.accelerometer.scaled)
        print("Accelerometer_angles: ", self.accelerometer.angle)

        print("-------------")
        print("Rocket")
        print("-------------")

        print("Rocket_angles: ", self.angle)

        print("Z acceleration: ", self.z_acceleration)

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

    def data_pack(self, sampling_rate):
        self.get_data(sampling_rate)
        return [round(self.xAngle, 1), round(self.yAngle, 1), round(self.zAngle, 1)]