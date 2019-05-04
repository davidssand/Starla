print("Initializing system...")

import threading
import sys
import time
import queue
import numpy as np
import pandas as pd
import operator
import math
import statistics

import sys
sys.path.append("/home/pi/Starla")
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

# ---------------------------- #

mpu = MPU6050()
bme = BME280()

# ---------------------------- #

soma = 0

print("Acc")
for i in range (0, 10):
  t0 = time.time()
  mpu.get_accelerometer_data()
  print(time.time() - t0)
  soma += time.time() - t0

print("Acc mean reading time: ", soma/10)

soma = 0
print("Gy")
for i in range (0, 10):
  t0 = time.time()
  mpu.get_gyroscope_data()
  print(time.time() - t0)
  soma += time.time() - t0

print("Gy mean reading time: ", soma/10)

soma = 0
print("MPU")
for i in range (0, 10):
  t0 = time.time()
  mpu.get_data(0.001)
  print(time.time() - t0)
  soma += time.time() - t0

print("MPU mean reading time: ", soma/10)

soma = 0
print("bme_list")
for i in range (0, 10):
  t0 = time.time()
  bme.get_data()
  print(time.time() - t0)
  soma += time.time() - t0

print("BME mean reading time: ", soma/10)

    





