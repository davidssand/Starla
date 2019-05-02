import threading
import sys
import time
import queue
import numpy as np
import pandas as pd
import operator
import math

def change_checker(valid_value, operator, validation_time):
  incoming_data = data_to_check.get()
  if operator(incoming_data, valid_value):
    print("---- VALID VALUE DETECTED ----\n")
    time_zero = time.time()
    while time.time() - time_zero < validation_time:
      incoming_data = data_to_check.get()
      print("Incoming data: ", incoming_data)
      if not operator(incoming_data, valid_value):
        print("---- DISTURBANCE ----\n")
        break
    else:
      print("Incoming data was valid for: ", time.time() - time_zero)
      return True

data_to_check = queue.Queue()

def check_change():
  while 1:
    change = False
    while not change:
      try:
        change = change_checker(-0.1, operator.lt, 1)
      except:
        print("Some error has occured")
    print("---- CHANGE STATE ----\n")

read_thread = threading.Thread(target=check_change, name = "Read and Decide", daemon=True)
read_thread.start()

x = np.linspace(-10, 10, num=200)
z_vel = np.sin(x)

for i in z_vel:
  data_to_check.put(i)
  time.sleep(0.1)