import RPi.GPIO as GPIO

class Parachute:
  # Activates parachute servo
  # Duty cycle = 50Hz
  # Period = 20ms
  # 0º -> 2.5% Duty cycle
  # 90º -> 7.5% Duty cycle
  # 180º -> 12.5% Duty cycle

  def __init__(self):
    self.gpio = GPIO
    self.gpio.setmode(self.gpio.BOARD)
    self.gpio.setup(12, self.gpio.OUT)

    self.servo = self.gpio.PWM(12, 50)

  def lock_parachute(self):
    self.servo.start(7.5)

  def activate_parachute(self):
    self.servo.ChangeDutyCycle(2.5)
  
  def deactivate_servo(self):
    self.servo.ChangeDutyCycle(0)