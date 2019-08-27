# Author : David Sand
# Date   : 18/05/2019
#
# --------------------------------------

# --- !!! Iniciates Rocket Telemetry !!! --- #


import sys
sys.path.append("/home/pi/Starla/Managers")
from rocket import Rocket

try:
  rocket = Rocket()
  rocket.main()
except KeyboardInterrupt:
  rocket.parachute.gpio.cleanup()
