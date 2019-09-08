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
import RPi.GPIO as GPIO
from datetime import datetime

import os
import sys
sys.path.append("/home/pi/Starla")
from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280

from Actuators.camera import Camera
from Actuators.parachute import Parachute
from Actuators.buzzer import Buzzer
from Actuators.button import Button

# ---------------------------- #
class Rocket:
  def __init__(self):
    print("Initializing system...")

    self.data_to_store = queue.Queue()
    self.data_to_check = queue.Queue()

    self.flight_datetime = datetime.utcnow().strftime("%m-%d-%Y_%H:%M:%S/")
    self.collected_data_path = "/home/pi/Starla/CollectedData/" + self.flight_datetime
    os.mkdir(self.collected_data_path)

    # self.camera = Camera()
    # self.parachute = Parachute()
    self.buzzer = Buzzer(12)
    self.button = Button(18)

    self.interval_storage_size = 3

    self.time_list = []
    self.validation_time = 1
    self.falling = False

    # MPU
    self.mpu = MPU6050()
    self.x_list = []
    self.y_list = []
    self.z_list = []
    self.valid_angulation = 0
    self.possible_angulation_fall = False
    self.mpu_status = []
    self.decision_angulation_time = 0

    #BME
    self.bme = BME280()
    self.altitude_list = []
    self.last_z_vel_value = 0
    self.z_velocity_list = [self.last_z_vel_value]
    self.bme_status = []
    self.valid_velocity = -0.5
    self.possible_velocity_fall = False
    self.decision_velocity_time = 0

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

    self.storage_thread = threading.Thread(target=self.store_data, name = "Store data", daemon=True)
    self.storage_thread.start()

  def store_data(self):
    # --------------- #

    # Store data in SD
    # Takes ≃ 100 ms to store

    # --------------- #

    while 1:
      incoming_data = self.data_to_store.get()
      t0 = time.time()

      df = pd.DataFrame({"time_list":  incoming_data["time_list"],
                          "altitude_list": incoming_data["altitude_list"],
                          "z_velocity_list": incoming_data["z_velocity_list"],
                          "x_list": incoming_data["x_list"],
                          "y_list": incoming_data["y_list"],
                          "z_list": incoming_data["z_list"],
                          "sr_list": incoming_data["sr_list"],
                          "mpu_status": incoming_data["mpu_status"],
                          "bme_status": incoming_data["bme_status"]})

      path = self.collected_data_path + "data.csv"
      df.to_csv(path, mode='a', header=False)
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
              "altitude_list": self.altitude_list,
              "z_velocity_list": self.z_velocity_list,
              "x_list": self.x_list,
              "y_list": self.y_list,
              "z_list": self.z_list,
              "sr_list": self.sr_list,
              "mpu_status": self.mpu_status,
              "bme_status": self.bme_status}

    self.data_to_store.put(package) 
    self.time_list = []
    self.altitude_list = []
    self.z_velocity_list = [self.last_z_vel_value]
    self.sr_list = [self.last_sr_value]
    self.x_list = []
    self.y_list = []
    self.z_list = []
    self.mpu_status = []
    self.bme_status = []

  def fall_decision(self):
    # --------------- #

    # Gathers all data in a package for decision

    # --------------- #
    y_accel = self.mpu.running_mean(self.y_list[-1])

    vel = (self.altitude_list[-1] - self.altitude_list[-2])/(self.time_list[-1] - self.time_list[-2])
    vel_filtered = self.running_mean(vel)
    self.z_velocity_list.append(vel_filtered)
    self.sr_list.append(self.time_list[-1]-self.time_list[-2])

    current_time = time.time()

    if not self.falling:
      self.change_checker("y_accel", y_accel, self.valid_angulation, self.decision_angulation_time, self.validation_time, self.possible_angulation_fall, current_time)
      self.change_checker("z_vel", vel_filtered, self.valid_velocity, self.decision_velocity_time, self.validation_time, self.possible_velocity_fall, current_time)

  def change_checker(self, responsible, data, valid_data, timer, valid_time, flag, current_time):
    flag = data <= valid_data

    if data <= valid_data and not flag:
      timer = current_time

    if ((current_time - timer) > valid_time) and flag:
      print("FALLING. RESPONSABILITY: " + responsible + "\n")
      flag = False
      self.buzzer.beep(0.5)
      self.falling = True
      self.log_fall(responsible)

  def log_fall(self, responsible):
    log_df = pd.DataFrame({"fall_time":  [self.time_list[-1]],
                            "z_velocity":  [self.z_velocity_list[-1]],
                            "y_acceleration":  [self.y_list[-1]],
                            "responsible": [responsible]})
    path = self.collected_data_path + "log.csv"
    log_df.to_csv(path, mode='a', header=False)

  def populate_data_arrays(self):
    # --------------- #

    # Puts read data in corresponding arrays
    
    # --------------- #

    self.mpu.get_data()
    self.bme.get_data()

    self.time_list.append(time.time() - self.system_time)

    self.x_list.append(self.mpu.accelerometer.scaled[0])
    self.y_list.append(self.mpu.accelerometer.scaled[1])
    self.z_list.append(self.mpu.accelerometer.scaled[2])

    self.altitude_list.append(self.bme.running_mean(self.bme.height))

    self.bme_status.append(self.bme.status)
    self.mpu_status.append(self.mpu.status)

  def initialize_csv_files(self):
    # --------------- #

    # Initiates data file with empty columns
    
    # --------------- #

    data_df = pd.DataFrame({"time_list":  [],
                            "altitude_list": [],
                            "z_velocity_list": [],
                            "x_list": [],
                            "y_list": [],
                            "z_list": [],
                            "sr_list": [],
                            "mpu_status": [],
                            "bme_status": []})

    path = self.collected_data_path + "data.csv"
    data_df.to_csv(path)

    log_df = pd.DataFrame({"fall_time":  [],
                            "z_velocity":  [],
                            "y_acceleration": [],
                            "responsible": []})

    path = self.collected_data_path + "log.csv"
    log_df.to_csv(path)

  def wait_start_command(self):
    while not self.button.pushed():
      pass
    self.buzzer.beep(0.5)
    
  def main(self):
    # --------------- #

    # Initiates system
    
    # --------------- #

    print("System ready!")
    self.buzzer.beep(0.5)

    self.wait_start_command()
    print("System initialized!")

    # self.camera.startRecording()
    # self.parachute.lock_parachute()
    self.initialize_csv_files()
    
    loop_time = 0
    while not self.button.pushed():
      self.populate_data_arrays()

      if len(self.time_list) > 1:
        self.fall_decision()

      if (self.time_list[-1] - loop_time) >= self.interval_storage_size:
        # resets loop time for entering in this condition again
        loop_time = self.time_list[-1]

        self.pack_store_data()

    print("System terminated!")
    GPIO.cleanup()
    self.buzzer.beep(1)
