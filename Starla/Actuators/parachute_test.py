from parachute_servo import ParachuteServo
import time

s1 = ParachuteServo(33)
s2 = ParachuteServo(32)

s1.setup()
s2.setup()

while 1:
  print("Type duty cycle period")
  duty_cycle = float(input()) 
  s1.test(duty_cycle)
  s2.test(duty_cycle)
