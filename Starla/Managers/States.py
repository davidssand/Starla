# !/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 21:03:57 2019

@author: David
"""
import sys
import numpy as np
import operator

sys.path.append("/home/pi/Starla")

from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280
from Actuators.Transmitter import Transmitter
from Actuators.Camera import Camera
from Actuators.Parachute import Parachute

mpu6050 = MPU6050()
bme280 = BME280()
transmitter = Transmitter()
camera = Camera()
parachute = Parachute()


class State:
  """
    General state
  """

  def __init__(self):
    print('Current state:', str(self))
    self.check_change()

  def check_change(self):
    pass

  def on_event(self):
    pass

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return self.__class__.__name__


class WaitingAscension(State):
  """
      Rocket has been ignited
  """

  def check_change(self):
      return change_checker(acceleration, valid_value, operator.gt, validation_time, self.on_event         

  def on_event(self):
      return ThrustedAscension()


class ThrustedAscension(State):
  """
      Rocket is acceleration upwards
  """
  def check_change(self):
    return change_checker(acceleration, valid_value, operator.lt, validation_time, self.on_event         

  def on_event(self):
    return DetectApogee()

class DetectFall(State):
  """

  """
  def check_change(self):
    return change_checker(z_velocity, 0, operator.lt, validation_time, self.on_event         

  def on_event(self):
    return Apogee()

class Apogee(State):
  """

  """

  def __init__(self):
    super().__init__()
    parachute.activate()
    self.on_event()

  def on_event(self):
    return FreeDescent()


class FreeDescent(State):
  """

  """

  def check_change(self):
    return change_checker(slowed_down_variabel, valid_value, operator.gt, validation_time, self.on_event:

  def on_event(self):
    return OpenedParachute()


class OpenedParachute(State):
  """
      Rocket hit the ground
  """

  def check_change(self):
    return change_checker(velocity, 0, operator.eq, validation_time, self.on_event:

  def on_event(self):
    return GroundHit()

class GroundHit(State):
    """
        Rocket hit the ground
    """

def change_checker(validation_variable, valid_value, operator, validation_time, returned):
  while 1:
    if operator(validation_variable, valid_value):
      time_zero = time.time()
      while time.time() - time_zero < validation_time:
        if operator(valid_value, validation_variable):
            break
      else:
        return returned()

