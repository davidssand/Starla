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

        # Filter
        # rm = running mean
        self.rm_lenght = 100
        self.rm_sum = 0
        self.rm_input_index = 0
        self.rm_result = [0 for _ in range(0, self.rm_lenght)]

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

    def get_accelerometer_data(self):
        self.accelerometer.raw[0] = self.read_word_2c(0x3b)
        self.accelerometer.raw[1] = self.read_word_2c(0x3d)
        self.accelerometer.raw[2] = self.read_word_2c(0x3f)

        self.accelerometer.scaled = self.accelerometer.scale(self.accelerometer.raw)
    
    def get_gyroscope_data(self):
        self.gyroscope.raw[0] = self.read_word_2c(0x43)
        self.gyroscope.raw[1] = self.read_word_2c(0x45)
        self.gyroscope.raw[2] = self.read_word_2c(0x47)

        self.gyroscope.scaled = -self.gyroscope.scale(self.gyroscope.raw)

    def get_rotation_rad(self, v):
        return [math.atan2(v[0], self.dist(v[1], v[2])) - math.pi/2.0,
         math.atan2(v[1], self.dist(v[0], v[2])) - math.pi/2.0,
         math.atan2(v[2], self.dist(v[0], v[1])) - math.pi/2.0]

        # return [math.atan2(v[i], self.dist(v[i==False], v[2-i//2])) - math.pi for i in range(0, 3)]

    def get_rotation_deg(self, v):
        return np.degrees(self.get_rotation_rad(v))
    
    def get_total_accel(self, accels):
        return np.sum(np.absolute(accels))

    # Complementary Filter
    def filtered_angle(self, sampling_rate, gyroscope_angle, accelerometer_angle):
        alpha = 1 / (1 + sampling_rate)
        return alpha * gyroscope_angle + (1 - alpha) * accelerometer_angle

    def get_data(self, sampling_rate):
        self.get_gyroscope_data()
        self.get_accelerometer_data()

        self.accelerometer.angle = self.get_rotation_deg(self.accelerometer.scaled)
        self.gyroscope.angle = self.angle + self.gyroscope.scaled * sampling_rate
        self.angle = self.filtered_angle(sampling_rate, self.gyroscope.angle, self.accelerometer.angle)     
        
        self.z_acceleration = self.get_total_accel(self.accelerometer.scaled)
        
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

    def data_pack(self, sampling_rate):
        self.get_data(sampling_rate)
        return [round(self.angle[0], 1), round(self.angle[1], 1), round(self.angle[2], 1)]

    def running_mean(self, data):
        self.rm_sum -= self.rm_result[self.rm_input_index]
        self.rm_result[self.rm_input_index] = data
        self.rm_sum += self.rm_result[self.rm_input_index]
        self.rm_input_index = (self.rm_input_index + 1) % self.rm_lenght

        # print("result", self.rm_result)
        # print("input_index", self.rm_input_index)
        # print("sum", self.rm_sum)

        return self.rm_sum/self.rm_lenght