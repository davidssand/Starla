import time
# import serial
import numpy as np
import pandas as pd

# import sys
# sys.path.append("/home/pi/Starla")
# from Sensors.GPS import GPS
# from Sensors.MPU6050 import MPU6050
# from Sensors.BME280 import BME280

# bme = BME280
# def get_z_vel():
#   while 1:
#     bme.get_data()
#     bme.hight

reads = [10, 12, 20, 13, 8, 11, 10, 30, 10, 12, 14, 15, 13, 5]

input_index = 0
result = [0 for x in range(0, 5)]
sum = 0
time_list = []
altitude = []
z_vel = []

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

t0 = time.time()
for i in range(len(reads)):
  altitude.append(running_mean(reads[i], 5))
  time_list.append(time.time() - t0)

z_vel = np.diff(altitude)
z_vel = np.append(z_vel, [z_vel[-1]])

print(time_list)
# print(altitude, len(altitude))
# print(z_vel, len(z_vel))

data = {"time":  time_list,
        "altitude": altitude,
        "z_velocity": z_vel}

df = pd.DataFrame.from_dict(data)

print(df)

df.to_csv(r'data.csv')