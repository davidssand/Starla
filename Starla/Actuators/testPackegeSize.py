#!/usr/bin/env python
import time
import serial

ser = serial.Serial(
               port='/dev/ttyAMA0',
               baudrate=9600,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=1
           )
n = 10
c = 0
t = 0.4
while 1:
    msg = '$' + str(n) + 'bytes' + (n-9) * '-' + '\n' + '#'
    ser.write(msg)
    print('sent')
    time.sleep(t)
    c += 1
    if c * t > 3:
        c = 0
        n += 10
