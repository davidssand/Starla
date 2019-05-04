print("Initializing system...")

import threading
import sys
import time
import queue
import numpy as np
import pandas as pd
import operator
import math


import sys
sys.path.append("/home/pi/Starla")
from Sensors.GPS import GPS
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

from Actuators.Transmitter import Transmitter
# ---------------------------- #

mpu = MPU6050()
bme = BME280()

while 1:
  time.sleep(0.5)
  mpu.get_data()
  

bme.get_data()
altitude.append(bme.running_mean(bme.hight))






