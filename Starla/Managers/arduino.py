#!/usr/bin/env python
import time
import numpy as np
from smbus2 import SMBusWrapper
 
# Give the I2C device time to settle
time.sleep(0.5)

class Arduino:
  def __init__(self):
    self.address = 0x75
    self.to_char = np.vectorize(chr)

  def get_data(self):
    with SMBusWrapper(1) as bus:
      try:
        block = bus.read_i2c_block_data(self.address, 0, 32)
        print(block)
        print()
        print("".join(self.to_char(block)))
        print()
      except Exception as ex:
        print(ex)
  
  def get_data_test(self, t = 0.5):
    while 1:
      self.get_data()
      time.sleep(t)