# !/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 21:03:57 2019

@author: David
"""
import sys
import numpy as np

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


class WaitingAscention(State):
    """
        Rocket has been ignited
    """

    change_checker(acceleration, valid_value, operator.gt, validation_time, self.on_event())         

    def on_event(self):
        return ThrustedAscention()


class ThrustedAscention(State):
    """
        Rocket is acceleration upwards
    """
    change_checker(acceleration, valid_value, operator.lt, validation_time, self.on_event())         

    def on_event(self):
        return DetectApogee()

class DetectFall(State):
    """

    """
    change_checker(z_velocity, valid_value, operator.lt, validation_time, self.on_event())         

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
        while (!slowed_down):
            pass

        self.on_event()

    def on_event(self):
        return OpenedParachute()


class OpenedParachute(State):
    """
        Rocket hit the ground
    """

    def check_change(self):
        while abs(velocity) > 0:
            pass

        self.on_event()

    def on_event(self):
        return GroundHit()

class GroundHit(State):
    """
        Rocket hit the ground
    """

def change_checker(validation_variable, valid_value, operator, validation_time, returned):
    if operator(validation_variable, valid_value):
        time_zero = time.time()
        while time.time() - time_zero < validation_time:
            if operator(valid_value, validation_variable):
                break
        else:
            return returned
        return None


