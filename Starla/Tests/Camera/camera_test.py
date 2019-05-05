print("Initializing system...")

import threading
import sys
import time
import queue
import numpy as np
import pandas as pd
import operator
import math


import sys
sys.path.append("/home/pi/Starla")
from Actuators.Camera import Camera

c = Camera()

t0 = time.time()
c.takePicture()
print("Picture took: ", time.time()-t0)

t0 = time.time()
c.startRecording()
print("start video took: ", time.time()-t0)

t0 = time.time()
c.stopRecording()
print("stop video took: ", time.time()-t0)
