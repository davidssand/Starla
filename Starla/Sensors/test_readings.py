import time

from MPU6050 import MPU6050
from BME280 import BME280

m = MPU6050()
b = BME280()

while(1):
  time.sleep(0.5)
  m.get_data()
  print("accel scaled: ", m.accelerometer.scaled)
  print("status: ", m.status)

  print("")

  b.get_data()
  print("height: ", b.height)
  print("status: ", b.status)

  print("")


