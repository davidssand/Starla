# !/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 21:03:57 2019

@author: David
"""

import time
import serial
import sys

sys.path.append("/home/pi/Starla")
from Managers.States import WaitingIgnition
from Managers.Thread import Thread
from Actuators.transmitter.Transmitter import Transmitter
from Managers.Rocket import Rocket

transmitter = Transmitter()

# --- Running program --- #


print("Iniciating system...")

dataSender = Thread("dataSender", transmitter.sendSensorsData, 0.45)

rocket = Rocket()
