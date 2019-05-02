import threading
import sys
import time
import queue

def check_change():
  global accel_list
  change = False
  while not change:
    try:
      change = change_checker(accel_list[-1], 1.5, operator.gt, 0.1)
    except:
      pass
  e.set()
  print("Change state")

def change_checker(validation_variable, valid_value, operator, validation_time):
  if operator(validation_variable, valid_value):
    time_zero = time.time()
    while time.time() - time_zero < validation_time:
      if operator(valid_value, validation_variable):
        break
    else:
      return True