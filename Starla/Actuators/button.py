import RPi.GPIO as GPIO

class Button:
  # Duty cycle standard = 5kHz

  def __init__(self, pinout):
    self.pinout = pinout
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(self.pinout, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # self.pushed = GPIO.add_event_detect(pinout, GPIO.FALLING, callback=self.pushed_event)  

  def pushed(self):
    return GPIO.input(self.pinout)
