import time
import numpy as np
import pandas as pd
import threading
import queue

import sys
sys.path.append("/home/pi/Starla")
from Sensors.GPS import GPS
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

# ---------------------------- #

storation_pack_size = 150

time_list = []
accel_list = []

altitude = []
last_z_vel_value = 0
z_vel = [last_z_vel_value]

data_to_store = queue.Queue()

def store_data():
  while 1:
    incoming_data = data_to_store.get()
    df = pd.DataFrame({"time":  incoming_data["time"],
                        "acceleration": incoming_data["acceleration"],
                        "altitude": incoming_data["altitude"],
                        "z_velocity": incoming_data["z_velocity"]})
    df.to_csv(r'data.csv', mode='a', header=False)
    print("data stored")

# ---------------------------- #

storage_thread = threading.Thread(target=store_data, name = "Store data")
storage_thread.start()

df = pd.DataFrame({"time":  [],
                  "acceleration": [],
                  "altitude": [],
                  "z_velocity": []})
df.to_csv(r'data.csv')

mpu = MPU6050()
bme = BME280()
t0 = time.time()

# ---------------------------- #
# Filter
# rm = running mean
rm_lenght = 50
rm_sum = 0
rm_input_index = 0
rm_result = [0 for _ in range(0, rm_lenght)]

def running_mean(data):
  global rm_sum, rm_result, rm_input_index, rm_lenght
  rm_sum -= rm_result[rm_input_index]
  rm_result[rm_input_index] = data
  rm_sum += rm_result[rm_input_index]
  rm_input_index = (rm_input_index + 1) % rm_lenght

  # print("result", rm_result)
  # print("input_index", rm_input_index)
  # print("sum", rm_sum)

  return rm_sum/rm_lenght

# ---------------------------- #

while 1:
  time.sleep(0.0001)
  if len(time_list) >= storation_pack_size:
    last_z_vel_value = z_vel[-1]
    package = {"time":  time_list,
              "acceleration": accel_list,
              "altitude": altitude,
              "z_velocity": z_vel}
    data_to_store.put(package) 
    time_list = []
    accel_list = []
    altitude = []
    z_vel = [last_z_vel_value]

  time_list.append(time.time() - t0)

  mpu.get_accelerometer_data()
  accel_list.append(mpu.get_total_accel(mpu.accelerometer.scaled))

  bme.get_data()
  altitude.append(bme.running_mean(bme.height))

  if len(time_list) > 1:
    vel = (altitude[-1] - altitude[-2])/(time_list[-1] - time_list[-2])
    z_vel.append(running_mean(vel))
