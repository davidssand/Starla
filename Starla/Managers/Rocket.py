import sys
import numpy as np

sys.path.append("/home/pi/Starla")

from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280
from Actuators.Transmitter import Transmitter
from Actuators.Camera import Camera
from Actuators.Parachute import Parachute

from Managers.Thread import Thread
from Managers.States import *

class Rocket:
  """
  State machine of rocket
  """

  def __init__(self):
    self.mpu6050 = MPU6050()
    self.bme280 = BME280()
    self.transmitter = Transmitter()
    self.camera = Camera()
    self.parachute = Parachute()

    activate_threads()
    detect_fall()

  def activate_threads(self):
    # Pipe throught states
    self.states_thread = Thread("Run thought states", states_pipe())

    # Transmites data
    self.transmitter_thread = Thread("Transmitting data", self.transmitter.start_transmition())     

    # Stores data
    self.storer_thread = Thread("Storing data"), self.store_data())

  def states_pipe(self):
    # Starting with a default state
    self.state = WaitingIgnition()
    self.state.check_change()

  def store_data(self):


  def detect_fall(self):
    is_falling = False
    change_checker(z_velocity, 0, operator.lt, validation_time, self.is_falling())
      
  def is_falling(self):
    self.state = Apogee()
    self.state.check_change()
