import time
import serial

import sys
sys.path.append("/home/pi/Starla")
from Sensors.GPS import GPS
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

class Tester:
    def __init__(self):
        self.bme280 = BME280()
        self.mpu6050 = MPU6050()
        self.gps = GPS()
        self.t = time.time()

    def show_sensor_data(self, sensor, delay):
        while True:
            time.sleep(delay)
            sensor.show_data(delay)
    
    def show_sensor_pack(self, sensor, delay):
        while True:
            time.sleep(delay)
            try:
                print(sensor.data_pack(delay))
            except:
                print(sensor.data_pack())

    def show_mpu_pack(self, delay):
        while True:
            time.sleep(delay)
            print("Filtered", self.mpu6050.data_pack(delay))
            print("Acc", self.mpu6050.accelerometer.angle)
            print("Gyro", self.mpu6050.gyroscope.angle)
            print()

t = Tester()
t.show_mpu_pack(0.3)