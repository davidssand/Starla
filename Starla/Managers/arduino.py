#!/usr/bin/env python
from time import sleep
import numpy as np
from smbus2 import SMBusWrapper
address = 0x75

 
# Give the I2C device time to settle
sleep(0.5)

to_char = np.vectorize(chr)

while 1:
  with SMBusWrapper(1) as bus:
    try:
      block = bus.read_i2c_block_data(address, 0, 32)
      print("".join(to_char(block)))
    except Exception as ex:
      print(ex)
    # data = bus.read_byte(address)
    # print("byte: ", data)
  
  # Decreasing delay may create more transmission errors.
  sleep(0.5)
