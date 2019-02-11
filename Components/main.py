# !/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 21:03:57 2019

@author: David
"""

import time
import serial
import sys

sys.path.append("/home/pi/Components")
from States.States import WaitingIgnition
from Thread import Thread
from transmitter.Transmitter import Transmitter
from Rocket.Rocket import Rocket

transmitter = Transmitter()

# --- Running program --- #


print("Iniciating system...")

dataSender = Thread("dataSender", transmitter.sendSensorsData, 0.45)

rocket = Rocket()
