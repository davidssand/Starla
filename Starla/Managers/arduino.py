#!/usr/bin/env python
from time import sleep
from smbus2 import SMBusWrapper
address = 0x75
 
# Give the I2C device time to settle
sleep(2)

while 1:
  with SMBusWrapper(1) as bus:
    block = bus.read_i2c_block_data(address, 0, 16)
    print("block: ", block)
    data = bus.read_byte(address)
    print("byte: ", data)
  
  # Decreasing delay may create more transmission errors.
  sleep(0.0005)
