# !/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 21:03:57 2019

@author: David
"""
import sys

sys.path.append("/home/pi/Components")

from MPU6050.MPU6050 import MPU6050
from BME280.BME280 import BME280
from Transmitter.Transmitter import Transmitter
from Camera.Camera import Camera
from Parachute import Parachute

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
        self.checkChange()

    def checkChange(self):
        pass

    def on_event(self):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__


class WaitingIgnition(State):
    """
        Waiting for ignition.
    """

    def on_event(self):
        return Ignited()


class Ignited(State):
    """
        Rocket has been ignited
    """

    def checkChange(self):
        while Acceleration < constant:
            pass

        self.on_event()

    def on_event(self):
        return ThrustedAscending()


class ThrustedAscending(State):
    """
        Rocket is acceleration upwards
    """

    def checkChange(self):
        while Acceleration > constant:
            pass

        self.on_event()

    def on_event(self):
        return FreeAscending()


class FreeAscending(State):
    """

    """

    def checkChange(self):
        while zVelocity > 0:
            pass

        self.on_event()

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

    def checkChange(self):
        while (!slowed_down):
            pass

        self.on_event()

    def on_event(self):
        return OpenedParachute()


class OpenedParachute(State):
    """
        Rocket hit the ground
    """

    def checkChange(self):
        while abs(velocity) > 0:
            pass

        self.on_event()

    def on_event(self):
        return GroundHit()

class GroundHit(State):
    """
        Rocket hit the ground
    """
