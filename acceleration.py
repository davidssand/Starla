import time
import numpy as np
import pandas as pd

import sys
sys.path.append("/home/pi/Starla")
from Sensors.GPS import GPS
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

# ------- Running Mean ------- #
N = 5
input_index = 0
result = [0 for x in range(0, N)]
sum = 0

def running_mean(data, N):
  global result, input_index, sum
  
  sum -= result[input_index]
  result[input_index] = data
  sum += result[input_index]
  input_index = (input_index + 1) % N

  # print("result", result)
  # print("input_index", input_index)
  # print("sum", sum)

  out_value = sum/N
  return out_value

# ---------------------------- #

storation_pack_size = 30

time_list = []
accel_list = []

df = pd.DataFrame({"acceleration": [],
                      "time":  []})
df.to_csv(r'mpu_data.csv')

mpu = MPU6050()
t0 = time.time()
z = 0
while 1:
  time.sleep(0.1)
  if len(time_list) >= storation_pack_size:
    df = pd.DataFrame({"acceleration": accel_list,
                      "time":  time_list})
    df.to_csv(r'mpu_data.csv', mode='a', header=False)
    print("mpu_data stored")
    time_list = []
    accel_list = []

  time_list.append(time.time() - t0)
  mpu.get_accelerometer_data()
  accels = mpu.accelerometer.scaled
  z = np.sum(np.absolute(accels))
  accel_list.append(running_mean(z, N))

