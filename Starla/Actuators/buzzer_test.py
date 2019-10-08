import RPi.GPIO as GPIO
import time

from buzzer import Buzzer
from button import Button

Button(18)
b = Buzzer(12)

while 1:
  if GPIO.input(18):
    b.beep()
