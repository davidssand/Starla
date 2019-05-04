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

# ---------------------------- #

data_to_store = queue.Queue()
data_to_check = queue.Queue()

# ---------------------------- #

def change_checker(valid_value, operator, validation_time):
  incoming_data = data_to_check.get()
  if operator(incoming_data, valid_value):
    print("---- VALID VALUE DETECTED ----\n")
    time_zero = time.time()
    while time.time() - time_zero < validation_time:
      incoming_data = data_to_check.get()
      print("Incoming data: ", incoming_data)
      if not operator(incoming_data, valid_value):
        print("---- DISTURBANCE ----\n")
        break
    else:
      print("Incoming data was valid for: ", time.time() - time_zero)
      return True

def check_change():
  while 1:
    change = False
    while not change:
      change = change_checker(-0.2, operator.lt, 0.1)
    print("---- CHANGE STATE ----\n")
    time.sleep(3)
    data_to_check.queue.clear()

# ---------------------------- #

def store_data():
  # Store data in SD
  # Storing rate ≃ 100 ms
  while 1:
    incoming_data = data_to_store.get()
    t0 = time.time()
    df = pd.DataFrame({"time":  incoming_data["time"],
                        "acceleration": incoming_data["acceleration"],
                        "altitude": incoming_data["altitude"],
                        "z_velocity": incoming_data["z_velocity"],
                        "sr_list": incoming_data["sr_list"]})
    df.to_csv(r'data.csv', mode='a', header=False)
    print("data stored, took:", time.time() - t0)

# ---------------------------- #

storage_thread = threading.Thread(target=store_data, name = "Store data")
storage_thread.start()
read_thread = threading.Thread(target=check_change, name = "Read and Decide")
read_thread.start()

df = pd.DataFrame({"time":  [],
                  "acceleration": [],
                  "altitude": [],
                  "z_velocity": [],
                  "sr_list": []})
df.to_csv(r'data.csv')

mpu = MPU6050()
bme = BME280()

# ---------------------------- #
# Filter
# rm = running mean
rm_lenght = 60
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

interval_storage_size = 3

time_list = []
accel_list = []

altitude = []
last_z_vel_value = 0
z_vel = [last_z_vel_value]

# sr -> sampling rate
last_sr_value = 0
sr_list = [last_sr_value]

print("System initialized!")
system_time = time.time()
loop_time = 0
while 1:
  time_list.append(time.time() - system_time)

  mpu.get_accelerometer_data()
  accel_list.append(mpu.get_total_accel(mpu.accelerometer.scaled))

  bme.get_data()
  altitude.append(bme.running_mean(bme.hight))

  if len(time_list) > 1:
    vel = (altitude[-1] - altitude[-2])/(time_list[-1] - time_list[-2])
    vel_filtered = running_mean(vel)
    z_vel.append(vel_filtered)
    data_to_check.put(vel_filtered)
    sr_list.append(time_list[-1]-time_list[-2])
  
  if (time_list[-1] - loop_time) >= interval_storage_size:

    last_sr_value = sr_list[-1]
    last_z_vel_value = z_vel[-1]

    # resets loop time for entering in this condition again
    loop_time = time_list[-1]

    # package sent to storing thread
    package = {"time":  time_list,
              "acceleration": accel_list,
              "altitude": altitude,
              "z_velocity": z_vel,
              "sr_list": sr_list}
    data_to_store.put(package) 
    time_list = []
    accel_list = []
    altitude = []
    z_vel = [last_z_vel_value]
    sr_list = [last_sr_value]





