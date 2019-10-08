import RPi.GPIO as GPIO
import time

class Buzzer:
  # Duty cycle standard = 5kHz

  def __init__(self, pinout, duty_cycle_frequency = 5000):
    self.pinout = pinout

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(self.pinout, GPIO.OUT)

    self.pwm = GPIO.PWM(self.pinout, duty_cycle_frequency)
    self.quiet_start()
  
  def quiet_start(self):
    self.pwm.start(0)

  def buzz(self):
    self.pwm.ChangeDutyCycle(30)

  def shut_up(self):
    self.pwm.ChangeDutyCycle(0)

  def beep(self, pause = 0.5):
    self.buzz()
    time.sleep(pause)
    self.shut_up()
  
  def cont_beep(self, pause = 0.5):
    GPIO.output(self.pinout, 1)
    time.sleep(pause)
    GPIO.output(self.pinout, 0)
  