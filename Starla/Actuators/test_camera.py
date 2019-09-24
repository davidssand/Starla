import RPi.GPIO as GPIO
import time

from camera import Camera
from button import Button

Button(18)

try:
  c = Camera()
except Exception as ex:
  print(ex)

while 1:
  if GPIO.input(18):
    try:
      capture(path + "time_" + str(int(time)) + ".jpg")
    except Exception as ex:
      print(ex)
