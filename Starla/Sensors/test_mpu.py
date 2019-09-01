import time

from MPU6050 import MPU6050

m = MPU6050()

while(1):
  time.sleep(0.1)
  m.get_accelerometer_data()
  print("accel scaled: ", m.accelerometer.scaled)
  print("accel angles: ", m.get_rotation_deg(m.accelerometer.scaled))