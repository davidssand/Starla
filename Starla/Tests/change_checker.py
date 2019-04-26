import time
import numpy as np
import operator

values = [10 for _ in range(0, 1000)] + [10 for _ in (range(1000))]

def change_checker(validation_variable, valid_value, operator, validation_time, returned):
  while 1:
    if operator(validation_variable, valid_value):
      t0 = time.time()
      while time.time() - t0 < validation_time:
        # if time.time() - t0 > 1:
        #   validation_variable -= 2
        print(time.time() - t0)
        if operator(valid_value, validation_variable):
            break
      else:
        return returned()
  
def foo():
  print("funfou")

m = 6
t1 = time.time()
change_checker(m, 5, operator.gt, 2, foo)