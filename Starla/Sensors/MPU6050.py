#!/usr/bin/python
import smbus
import math
import sys

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
        
        self.acelerometer = self.Acelerometer()
        self.gyroscope = self.Gyroscope()

        self.angle = [0, 0, 0]

    class Acelerometer:
        def __init__(self):
            self.raw = [0, 0, 0]
            self.scaled = [0, 0, 0]
            self.angle = [0, 0, 0]

        def scale(self, a):
            return a / 16384.0  # Convert to G's

    class Gyroscope:
        def __init__(self):
            self.vel_raw = [0, 0, 0]
            self.vel_scaled = [0, 0, 0]
            self.angle = [0, 0, 0]

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

    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)
    
    # Complementary Filter
    def filtered_angle(self, sampling_rate, gyroscope_angle, acelerometer_angle):
        alpha = 1 / (1 + sampling_rate)
        return alpha * gyroscope_angle + (1 - alpha) * acelerometer_angle

    def get_raw_data(self):
        self.gyroscope.vel_raw[0] = self.read_word_2c(0x43)
        self.gyroscope.vel_raw[1] = self.read_word_2c(0x45)
        self.gyroscope.vel_raw[2] = self.read_word_2c(0x47)
        self.acelerometer.raw[0] = self.read_word_2c(0x3b)
        self.acelerometer.raw[1] = self.read_word_2c(0x3d)
        self.acelerometer.raw[2] = self.read_word_2c(0x3f)
    
    def get_data(self, sampling_rate):
        self.get_raw_data()

        self.acelerometer.angle[0] = self.get_x_rotation(self.acelerometer.scaled[0], self.acelerometer.scaled[1], self.acelerometer.scaled[2])
        self.acelerometer.angle[1] = self.get_y_rotation(self.acelerometer.scaled[0], self.acelerometer.scaled[1], self.acelerometer.scaled[2])
        self.acelerometer.angle[2] = 0     # No magnetometer data

        for i in range(0, 3):
            self.gyroscope.vel_scaled[i] = self.gyroscope.scale(self.gyroscope.vel_raw[i])
            self.gyroscope.angle[i] = self.angle[i] + self.gyroscope.vel_scaled[i] * sampling_rate
            self.acelerometer.scaled[i] = self.acelerometer.scale(self.acelerometer.raw[i])
            self.angle[i] = self.filtered_angle(sampling_rate, self.gyroscope.angle[i], self.acelerometer.angle[i])            
        
    def show_data(self, sampling_rate):
        self.get_data(sampling_rate)

        print("-------------")
        print("Gyroscope_angles")
        print("-------------")

        print("Gyroscope_x: ", self.gyroscope.angle[0])
        print("Gyroscope_y: ", self.gyroscope.angle[1])
        print("Gyroscope_z: ", self.gyroscope.angle[2])

        print("-------------")
        print("Acelerometer_angles")
        print("-------------")

        print("Acelerometer_x: ", self.acelerometer.angle[0])
        print("Acelerometer_y: ", self.acelerometer.angle[1])
        print("Acelerometer_z: ", self.acelerometer.angle[2])

        print("-------------")
        print("Rocket_angle")
        print("-------------")

        print("X Rotation: ", self.angle[0])
        print("Y Rotation: ", self.angle[1])
        print("Y Rotation: ", self.angle[2])    # Do not trust

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