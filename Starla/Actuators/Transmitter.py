import time
import serial

import sys
sys.path.append("/home/pi/Starla")
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

BME280 = BME280()
MPU6050 = MPU6050()
t = time.time()

class Transmitter:
    def __init__(self):
        self.ser = serial.Serial(
                    port="/dev/ttyAMA0",
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1
                   )

    def send_data_test(self):
        msg = ""
        msg += str(round(time.time()-t, 2)) + ","
        c = ""
        for i in range(len(MPU6050.dataPackage())):
            msg += c + str(MPU6050.dataPackage()[i])
            c = ","
        for i in range(len(BME280.dataPackage())):
            msg += c + str(BME280.dataPackage()[i])
            c = ","
        self.ser.write(msg)
        print(msg + "\n")
        msg = ""

    def send_data(self, data):
        msg = ""
        msg += str(round(time.time()-t, 2)) + ","
        c = ""
        for i in range(len(MPU6050.dataPackage())):
            msg += c + str(MPU6050.dataPackage()[i])
            c = ","
        for i in range(len(BME280.dataPackage())):
            msg += c + str(BME280.dataPackage()[i])
            c = ","
        self.ser.write(msg)
        print(msg + "\n")
        msg = ""