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

from Actuators.Camera import Camera
from Actuators.Parachute import Parachute

# ---------------------------- #
class Rocket:
  def __init__(self):
    self.data_to_store = queue.Queue()
    self.data_to_check = queue.Queue()

    self.camera = Camera()
    self.parachute = Parachute()

    self.mpu = MPU6050()
    self.bme = BME280()

    # ---------------------------- #
    # Filter
    # rm = running mean
    self.rm_lenght = 60
    self.rm_sum = 0
    self.rm_input_index = 0
    self.rm_result = [0 for _ in range(0, self.rm_lenght)]

    self.iniciate_threads()

  # ---------------------------- #

  def iniciate_threads(self):
    self.storage_thread = threading.Thread(target=self.store_data, name = "Store data")
    self.storage_thread.start()
    self.read_thread = threading.Thread(target=self.check_change, name = "Read and Decide")
    self.read_thread.start()

  def change_checker(self, valid_value, operator, validation_time):
    incoming_data = self.data_to_check.get()
    if operator(incoming_data, valid_value):
      print("---- VALID VALUE DETECTED ----\n")
      time_zero = time.time()
      while time.time() - time_zero < validation_time:
        incoming_data = self.data_to_check.get()
        print("Incoming data: ", incoming_data)
        if not operator(incoming_data, valid_value):
          print("---- DISTURBANCE ----\n")
          break
      else:
        print("Incoming data was valid for: ", time.time() - time_zero)
        return True

  def check_change(self):
    while 1:
      change = False
      while not change:
        change = self.change_checker(-0.2, operator.lt, 0.1)
      print("---- CHANGE STATE ----\n")
      self.camera.takePicture()
      self.parachute.activate()

      #### For tests ####
      time.sleep(3)
      self.data_to_check.queue.clear()

  def store_data(self):
    # Store data in SD
    # Takes ≃ 100 ms to store
    while 1:
      incoming_data = self.data_to_store.get()
      t0 = time.time()
      df = pd.DataFrame({"time":  incoming_data["time"],
                          "acceleration": incoming_data["acceleration"],
                          "altitude": incoming_data["altitude"],
                          "z_velocity": incoming_data["z_velocity"],
                          "pitch": incoming_data["pitch"],
                          "yaw": incoming_data["yaw"],
                          "roll": incoming_data["roll"],
                          "sr_list": incoming_data["sr_list"]})
      df.to_csv(r'data.csv', mode='a', header=False)
      print("data stored, took:", time.time() - t0)

  def running_mean(self, data):
    self.rm_sum -= self.rm_result[self.rm_input_index]
    self.rm_result[self.rm_input_index] = data
    self.rm_sum += self.rm_result[self.rm_input_index]
    self.rm_input_index = (self.rm_input_index + 1) % self.rm_lenght

    # print("result", self.rm_result)
    # print("input_index", self.rm_input_index)
    # print("sum", self.rm_sum)

    return self.rm_sum/self.rm_lenght

  def decider(self):
    df = pd.DataFrame({"time":  [],
                      "acceleration": [],
                      "altitude": [],
                      "z_velocity": [],
                      "pitch": [],
                      "yaw": [],
                      "roll": [],
                      "sr_list": []})
    df.to_csv(r'data.csv')

    interval_storage_size = 3

    time_list = []

    accel_list = []
    pitch_list = []
    yaw_list = []
    roll_list = []

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

      self.mpu.get_data(0.025)
      accel_list.append(self.mpu.get_total_accel(self.mpu.accelerometer.scaled))
      pitch_list.append(self.mpu.angle[0])
      yaw_list.append(self.mpu.angle[1])
      roll_list.append(self.mpu.angle[2])

      self.bme.get_data()
      altitude.append(self.bme.running_mean(self.bme.hight))

      if len(time_list) > 1:
        vel = (altitude[-1] - altitude[-2])/(time_list[-1] - time_list[-2])
        vel_filtered = self.running_mean(vel)
        z_vel.append(vel_filtered)
        self.data_to_check.put(vel_filtered)
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
                  "pitch": pitch_list,
                  "yaw": yaw_list,
                  "roll": roll_list,
                  "sr_list": sr_list}
        self.data_to_store.put(package) 
        time_list = []
        accel_list = []
        altitude = []
        z_vel = [last_z_vel_value]
        sr_list = [last_sr_value]
        pitch_list = []
        yaw_list = []
        roll_list = []


rocket = Rocket()
rocket.decider()


