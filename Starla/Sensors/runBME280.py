import sys
sys.path.append("/home/pi/Starla")

from Sensors.BME280 import BME280
import time

sensor = BME280()
while 1:
    time.sleep(1)
    sensor.showData()
    print(sensor.dataPackage())

