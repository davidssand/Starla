import RPi.GPIO as GPIO

class ParachuteServo:
  # Activates parachute servo
  # Duty cycle = 50Hz
  # Period = 20ms
  # 0º -> 2.5% Duty cycle
  # 90º -> 7.5% Duty cycle
  # 180º -> 12.5% Duty cycle

  def __init__(self, pinout):
    self.gpio = GPIO
    self.gpio.setmode(self.gpio.BOARD)
    self.gpio.setup(pinout, self.gpio.OUT)

    self.servo = self.gpio.PWM(pinout, 50)

  def setup(self):
    self.servo.start(2.5)

  def lock(self):
    self.servo.ChangeDutyCycle(9)

  def activate(self):
    self.servo.ChangeDutyCycle(2.5)
  
  def deactivate(self):
    self.servo.ChangeDutyCycle(0)