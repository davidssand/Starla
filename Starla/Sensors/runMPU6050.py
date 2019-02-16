from MPU6050_Readings import MPU6050
import time

sensor = MPU6050()
while 1:
    for i in range(len(sensor.dataPackage())):
        print sensor.dataPackage()[i]
    time.sleep(0.1)
    sensor.showData()
    print sensor.dataPackage()

