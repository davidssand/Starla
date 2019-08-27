import RPi.GPIO as GPIO
import time

class Buzzer:
  # Duty cycle standard = 5kHz

  def __init__(self, pinout, duty_cycle_frequency = 5000):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pinout, GPIO.OUT)

    self.pwm = GPIO.PWM(pinout, duty_cycle_frequency)
    self.quiet_start()
  
  def quiet_start(self):
    self.pwm.start(0)

  def buzz(self):
    self.pwm.ChangeDutyCycle(50)

  def shut_up(self):
    self.pwm.ChangeDutyCycle(0)

  def beep(self, pause):
    self.buzz()
    time.sleep(pause)
    self.shut_up()
  