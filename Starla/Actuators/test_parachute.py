from parachute_servo import ParachuteServo
import time

p_1 = ParachuteServo(33)
p_2 = ParachuteServo(32)
p_1.lock()
p_2.lock()
time.sleep(2)
p_1.activate()
p_2.activate()
time.sleep(2)