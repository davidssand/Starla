# Author : David Sand
# Date   : 18/05/2019
#
# --------------------------------------

# --- !!! Iniciates Rocket Telemetry !!! --- #

import RPi.GPIO as GPIO
import sys
sys.path.append("/home/pi/Starla/Beta")
from rocket_mpu_decision import Rocket

try:
  rocket = Rocket()
  rocket.main()
except KeyboardInterrupt:
  GPIO.cleanup()
