import time
import numpy as np
import pandas as pd
import operator

import sys
sys.path.append("/home/pi/Starla")
from Sensors.GPS import GPS
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

from Managers.Thread import Thread

# ---------------------------- #

storation_pack_size = 150

time_list = []
accel_list = []

altitude = []
z_vel = []
last_z_vel_value = 0

df = pd.DataFrame({"time":  [],
                  "acceleration": [],
                  "altitude": [],
                  "z_velocity": []})
df.to_csv(r'data.csv')

mpu = MPU6050()
bme = BME280(50)
t0 = time.time()
z = 0

change_thread = Thread("Check_change", check_change())

while 1:
  time.sleep(0.0001)
  if len(time_list) >= storation_pack_size:
    z_vel = np.append(last_z_vel_value, np.diff(altitude))
    last_z_vel_value = z_vel[-1]
    df = pd.DataFrame({"time":  time_list,
                      "acceleration": accel_list,
                      "altitude": altitude,
                      "z_velocity": z_vel})
    df.to_csv(r'data.csv', mode='a', header=False)
    print("data stored")
    time_list = []
    accel_list = []
    altitude = []
    z_vel = []

  time_list.append(time.time() - t0)

  mpu.get_accelerometer_data()
  z = mpu.get_total_accel(mpu.accelerometer.scaled)
  accel_list.append(z)

  bme.get_data()
  altitude.append(bme.running_mean(bme.hight))

def check_change(self):
  global accel_list
  change = False
  while not change:
    try:
      change = change_checker(accel_list[-1], 1.5, operator.gt, 0.1)
    except:
      pass
  print("Change state")

def change_checker(validation_variable, valid_value, operator, validation_time):
  if operator(validation_variable, valid_value):
    time_zero = time.time()
    while time.time() - time_zero < validation_time:
      if operator(valid_value, validation_variable):
        break
    else:
      return True