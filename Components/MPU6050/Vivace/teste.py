from vivace import MPU
import time

sensor = MPU()
while 1:
    time.sleep(1)
    print sensor.getAcz()
