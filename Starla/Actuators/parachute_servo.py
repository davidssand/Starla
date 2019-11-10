import RPi.GPIO as GPIO

class ParachuteServo:
  # Activates parachute servos

  # Duty cycle frequency = 50Hz
  # Period = 20ms

  # Duty cycle is in percentage

  # 0º -> 2.5% Duty cycle
  # 90º -> 7.5% Duty cycle
  # 180º -> 12.5% Duty cycle

  def __init__(self, pinout):
    self.gpio = GPIO
    self.gpio.setmode(self.gpio.BOARD)
    self.gpio.setup(pinout, self.gpio.OUT)

    self.servo = self.gpio.PWM(pinout, 50)

  def setup(self):
    self.servo.start(4)

  def lock(self):
    self.servo.ChangeDutyCycle(8)

  def activate(self):
    self.servo.ChangeDutyCycle(4)
  
  def detach(self):
    self.servo.ChangeDutyCycle(0)

  def test(self, duty_cycle):
    self.servo.ChangeDutyCycle(duty_cycle)
