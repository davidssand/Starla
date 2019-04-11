import time
import serial
import numpy as np

import sys
sys.path.append("/home/pi/Starla")
from Sensors.GPS import GPS
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

class Tester:
  def __init__(self):
    self.mpu = MPU6050()

  def get_max_z_acceleration(self, test_interval):
    t0 = time.time()
    m = [1, time.time()-t0]
    while (time.time() - t0) < test_interval:
        accels = self.mpu.get_accelerometer_data()
        z = np.sum(np.absolute(accels))
        m[0] = max(m[0], z)
        m[1] = time.time() - t0
    return m