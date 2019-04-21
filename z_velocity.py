import time
import numpy as np
import pandas as pd

import serial
import sys
sys.path.append("/home/pi/Starla")
from Sensors.GPS import GPS
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

# ------- Running Mean ------- #
N = 30
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
temp_list = []
pressure_list = []
altitude = []
z_vel = []
last_z_vel_value = 0

df = pd.DataFrame({"altitude": [],
                      "time":  [],
                      "z_velocity": [],
                      "temp_list": [],
                      "pressure_list": []})
df.to_csv(r'bme_data.csv')

bme = BME280()
t0 = time.time()
while 1:
  time.sleep(0.1)
  if len(time_list) >= storation_pack_size:
    z_vel = np.append(last_z_vel_value, np.diff(altitude))
    last_z_vel_value = z_vel[-1]
    df = pd.DataFrame({"time":  time_list,
                      "altitude": altitude,
                      "z_velocity": z_vel,
                      "temperature": temp_list,
                      "pressure": pressure_list})
    df.to_csv(r'bme_data.csv', mode='a', header=False)
    print("bme_data stored")
    time_list = []
    temp_list = []
    pressure_list = []
    altitude = []
    z_vel = []

  time_list.append(time.time() - t0)
  bme.get_data()
  altitude.append(running_mean(bme.hight, N))
  temp_list.append(bme.temperature)
  pressure_list.append(bme.pressure)
