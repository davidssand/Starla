#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("Importing libs")
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

from Actuators.camera import Camera
from Actuators.parachute import Parachute

# ---------------------------- #
class Rocket:
  def __init__(self):
    print("Initializing system...")

    self.data_to_store = queue.Queue()
    self.data_to_check = queue.Queue()

    self.camera = Camera()
    self.parachute = Parachute()

    self.mpu = MPU6050()
    self.bme = BME280()

    self.interval_storage_size = 3

    self.time_list = []

    self.accel_list = []
    self.pitch_list = []
    self.yaw_list = []
    self.roll_list = []

    self.altitude_list = []
    self.last_z_vel_value = 0
    self.z_velocity_list = [self.last_z_vel_value]

    # sr -> sampling rate
    self.last_sr_value = 0
    self.sr_list = [self.last_sr_value]

    # ---------------------------- #
    # Filter
    # rm = running mean
    self.rm_lenght = 60
    self.rm_sum = 0
    self.rm_input_index = 0
    self.rm_result = [0 for _ in range(0, self.rm_lenght)]

    self.iniciate_threads()

    self.system_time = time.time()
  # ---------------------------- #

  def iniciate_threads(self):
    # --------------- #

    # Iniciates all system threads

    # --------------- #

    self.storage_thread = threading.Thread(target=self.store_data, name = "Store data")
    self.storage_thread.start()
    self.decision_thread = threading.Thread(target=self.check_change, name = "Read and Decide")
    self.decision_thread.start()

  def change_checker(self, valid_value, operator, validation_time):
    # --------------- #

    # Check for valid change in input variable

    # --------------- #

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
    # --------------- #

    # Decides when to open parachute

    # --------------- #

    while 1:
      change = False
      while not change:
        change = self.change_checker(-0.2, operator.lt, 0.15)
      print("---- CHANGE STATE ----\n")
      self.camera.take_picture()
      self.parachute.activate_parachute()

      #### For tests ####
      time.sleep(3)
      self.camera.stopRecording()
      self.parachute.deactivate_servo()
      self.data_to_check.queue.clear()

  def store_data(self):
    # --------------- #

    # Store data in SD
    # Takes ≃ 100 ms to store

    # --------------- #

    while 1:
      incoming_data = self.data_to_store.get()
      t0 = time.time()
      df = pd.DataFrame({"time_list":  incoming_data["time_list"],
                          "acceleration_list": incoming_data["acceleration_list"],
                          "altitude_list": incoming_data["altitude_list"],
                          "z_velocity_list": incoming_data["z_velocity_list"],
                          "pitch_list": incoming_data["pitch_list"],
                          "yaw_list": incoming_data["yaw_list"],
                          "roll_list": incoming_data["roll_list"],
                          "sr_list": incoming_data["sr_list"]})
      df.to_csv(r'data.csv', mode='a', header=False)
      print("data stored, took:", time.time() - t0)

  def running_mean(self, data):
    # --------------- #

    # Running mean for velocity

    # --------------- #
    self.rm_sum -= self.rm_result[self.rm_input_index]
    self.rm_result[self.rm_input_index] = data
    self.rm_sum += self.rm_result[self.rm_input_index]
    self.rm_input_index = (self.rm_input_index + 1) % self.rm_lenght

    # print("result", self.rm_result)
    # print("input_index", self.rm_input_index)
    # print("sum", self.rm_sum)

    return self.rm_sum/self.rm_lenght

  def pack_store_data(self):
    # --------------- #

    # Gathers all data in a package for storage_thread

    # --------------- #

    self.last_sr_value = self.sr_list[-1]
    self.last_z_vel_value = self.z_velocity_list[-1]

    # package sent to storing thread
    package = {"time_list":  self.time_list,
              "acceleration_list": self.accel_list,
              "altitude_list": self.altitude_list,
              "z_velocity_list": self.z_velocity_list,
              "pitch_list": self.pitch_list,
              "yaw_list": self.yaw_list,
              "roll_list": self.roll_list,
              "sr_list": self.sr_list}
    self.data_to_store.put(package) 
    self.time_list = []
    self.accel_list = []
    self.altitude_list = []
    self.z_velocity_list = [self.last_z_vel_value]
    self.sr_list = [self.last_sr_value]
    self.pitch_list = []
    self.yaw_list = []
    self.roll_list = []
  
  def pack_decision_data(self):
    # --------------- #

    # Gathers all data in a package for decision_thread

    # --------------- #

    vel = (self.altitude_list[-1] - self.altitude_list[-2])/(self.time_list[-1] - self.time_list[-2])
    vel_filtered = self.running_mean(vel)
    self.z_velocity_list.append(vel_filtered)
    self.data_to_check.put(vel_filtered)
    self.sr_list.append(self.time_list[-1]-self.time_list[-2])
  
  def populate_data_arrays(self):
    # --------------- #

    # Puts read data in corresponding arrays
    
    # --------------- #

    self.mpu.get_data(0.03)
    self.bme.get_data()

    self.time_list.append(time.time() - self.system_time)
    self.accel_list.append(self.mpu.get_total_accel(self.mpu.accelerometer.scaled))
    self.pitch_list.append(self.mpu.angle[0])
    self.yaw_list.append(self.mpu.angle[1])
    self.roll_list.append(self.mpu.angle[2])
    self.altitude_list.append(self.bme.running_mean(self.bme.hight))

  def initialize_csv_file(self):
    # --------------- #

    # Initiates data file with empty columns
    
    # --------------- #

    df = pd.DataFrame({"time_list":  [],
                      "acceleration_list": [],
                      "altitude_list": [],
                      "z_velocity_list": [],
                      "pitch_list": [],
                      "yaw_list": [],
                      "roll_list": [],
                      "sr_list": []})
    df.to_csv(r'data.csv')

  def main(self):
    # --------------- #

    # Initiates system
    
    # --------------- #

    print("System initialized!")

    self.camera.startRecording()
    self.parachute.lock_parachute()
    self.initialize_csv_file()
    
    loop_time = 0
    while 1:
      self.populate_data_arrays()

      if len(self.time_list) > 1:
        self.pack_decision_data()

      if (self.time_list[-1] - loop_time) >= self.interval_storage_size:
        # resets loop time for entering in this condition again
        loop_time = self.time_list[-1]

        self.pack_store_data()
