import sys
import numpy as np

sys.path.append("/home/pi/Starla")

from Sensors.MPU6050 import MPU6050
from Sensors.BME280 import BME280
from Actuators.Transmitter import Transmitter
from Actuators.Camera import Camera
from Actuators.Parachute import Parachute

from Managers.Thread import Thread
from Managers.States import WaitingIgnition
from Managers.States import DetectFall

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
    
        # Pipe throught states
        states_thread = Thread("Run thought states", states_pipe())

        # Transmites data
        transmitter_thread = Thread("Transmitting data", self.transmitter.start_transmition())      

        while self.state == WaitingIgnition():
            pass
        else:
            # Spare thread for detecting fall
            fall_detection_thread = Thread("Fall detector", detect_fall())

        def states_pipe():
            # Starting with a default state
            self.state = WaitingIgnition()
            self.state.check_change()

        def detect_fall(self):
            while 1:
                if z_velocity < 0:
                    time_zero = time.time()
                    while time.time() - time_zero < data_validation_time:
                        if z_velocity > 0:
                            break
                    else:
                        is_falling == True
            
        
