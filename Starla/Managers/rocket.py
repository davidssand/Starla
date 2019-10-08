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
from Actuators.parachute_servo import ParachuteServo
from Actuators.buzzer import Buzzer
from Actuators.button import Button
from Managers.arduino import Arduino

# ---------------------------- #
class Rocket:
  def __init__(self):
    print("Initializing system...")

    self.data_to_store = queue.Queue()

    self.flight_datetime = datetime.now().strftime("%m-%d-%Y_%H:%M:%S/")
    self.collected_data_path = "/home/pi/Starla/CollectedData/" + self.flight_datetime
    os.mkdir(self.collected_data_path)

    self.instantiate_parts()

    self.setup_bme()
    self.setup_mpu()

    # sr -> sampling rate
    self.last_sr_value = 0
    self.sr_list = [self.last_sr_value]

    self.setup_running_mean()

    self.iniciate_threads()

    self.interval_storage_size = 3
    self.time_list = []
    self.validation_time = 1
    self.falling = False
    self.system_time = 0
  # ---------------------------- #

  def instantiate_parts(self):
    self.camera = Camera()
    self.servo_1 = ParachuteServo(32)
    self.servo_2 = ParachuteServo(33)
    self.buzzer = Buzzer(12)
    self.button = Button(18)
    self.bme = BME280()
    self.mpu = MPU6050()
    self.arduino = Arduino()

  def setup_running_mean(self):
    # rm = running mean
    self.rm_lenght = 60
    self.rm_sum = 0
    self.rm_input_index = 0
    self.rm_result = [0 for _ in range(0, self.rm_lenght)]

  def setup_bme(self):
    self.altitude_list = []
    self.last_z_vel_value = 0
    self.z_velocity_list = [self.last_z_vel_value]
    self.bme_status = []
    self.valid_velocity = -0.5
    self.possible_velocity_fall = False
    self.decision_velocity_time = 0

  def setup_mpu(self):
    self.x_list = []
    self.y_list = []
    self.z_list = []
    self.valid_acceleration = 0
    self.possible_acceleration_fall = False
    self.mpu_status = []
    self.decision_acceleration_time = 0


  def iniciate_threads(self):
    # --------------- #

    # Iniciates all system threads

    # --------------- #

    self.storage_thread = threading.Thread(target=self.store_data, name = "Storage thread", daemon=True)
    self.storage_thread.start()

    self.parachute_thread = threading.Thread(target=self.parachute_actions, name = "Parachute thread", daemon=True)
    self.parachute_thread.start()
    self.deactivate_servos_event = threading.Event()

  def parachute_actions(self):
    while(1):
      self.deactivate_servos_event.wait()
      time.sleep(1)
      self.deactivate_servos()

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
    self.reset_arrays()

  def reset_arrays(self):
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


    if not self.falling:
      self.accel_change_checker("y_accel", y_accel)
      self.vel_change_checker("z_vel", vel_filtered)

  def accel_change_checker(self, responsible, y_accel):
    current_time = time.time()

    self.possible_acceleration_fall = y_accel <= self.valid_acceleration

    if not self.possible_acceleration_fall:
      self.decision_acceleration_time = current_time

    if ((current_time - self.decision_acceleration_time) > self.validation_time):
      print("FALLING. RESPONSABILITY: " + responsible + "\n")
      self.possible_acceleration_fall = False
      self.fall_actions(responsible)

  def vel_change_checker(self, responsible, vel_filtered):
    current_time = time.time()

    self.possible_velocity_fall = vel_filtered <= self.valid_velocity

    if not self.possible_velocity_fall:
      self.decision_velocity_time = current_time

    if ((current_time - self.decision_velocity_time) > self.validation_time):
      print("FALLING. RESPONSABILITY: " + responsible + "\n")
      self.possible_velocity_fall = False
      self.fall_actions(responsible)
      
  def fall_actions(self, responsible):
    self.open_parachute()
    self.buzzer.beep()
    self.falling = True
    self.log_fall(responsible)
    self.camera.takePicture(self.collected_data_path, self.time_list[-1])
    self.deactivate_servos_event.set()

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
    while 1:
      if input() == "launch":
        break
      else:
        print("To launch, type 'launch'")

  def setup_parachute_servos(self):
    self.servo_1.setup()
    self.servo_2.setup()

  def lock_parachute(self):
    self.servo_1.lock()
    self.servo_2.lock()

  def open_parachute(self):
    self.servo_1.activate()
    self.servo_2.activate()

  def deactivate_servos(self):
    self.servo_1.deactivate()
    self.servo_2.deactivate()

  def main(self):
    # --------------- #

    # Initiates system
    
    # --------------- #

    self.buzzer.beep()
    self.setup_parachute_servos()

    print("System ready\nType 'launch' to launch")

    self.wait_start_command()
    self.buzzer.beep()
    print("System initialized and running")

    self.system_time = time.time()

    # self.camera.startRecording()
    self.lock_parachute()
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

    self.buzzer.beep(0.3)
    time.sleep(0.3)
    self.buzzer.beep(0.3)
    print("System terminated!")
    GPIO.cleanup()
