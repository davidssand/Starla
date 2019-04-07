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
            try:
                sensor.show_data(delay)
            except:
                sensor.show_data()
    
    def test_sensor(self, sensor):
        print("Testing " + str(sensor))
        msg = ""
        c = ""
        for i in range(len(sensor.data_pack())):
            msg += c + str(sensor.data_pack()[i])
            c = ","
        return msg

    def test_sensors_pack(self):
        msg = "$"
        msg += str(round(time.time() - self.t, 2)) + ","
        msg += self.test_sensor(self.mpu6050)
        msg += self.test_sensor(self.bme280)
        msg += self.test_sensor(self.gps)
        msg += "#\n"
        return msg

