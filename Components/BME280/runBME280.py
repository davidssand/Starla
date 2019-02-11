from BME280_Readings import BME280
import time

sensor = BME280()
while(1):
    time.sleep(1)
    sensor.showData()
    print sensor.dataPackage()

