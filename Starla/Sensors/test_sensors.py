import time
import serial

import sys
sys.path.append("/home/pi/Starla")
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

class TestSensors:
    def __init__(self):
        self.bme280 = BME280()
        self.mpu6050 = MPU6050()
        self.t = 0

    def show_sensors_pack(self, delay):
        self.t = time.time()
        while 1:
            msg = "$"
            msg += str(round(time.time() - self.t, 2)) + ","
            c = ""
            for i in range(len(self.mpu6050.dataPackage())):
                msg += c + str(self.mpu6050.dataPackage()[i])
                c = ","
            for i in range(len(self.bme280.dataPackage())):
                msg += c + str(self.bme280.dataPackage()[i])
                c = ","
            msg += "#"
            print(msg + "\n")
            msg = ""
            time.sleep(delay)
