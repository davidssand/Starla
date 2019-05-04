import threading
import sys
import time
import queue

def sleeper():
  while 1:
    print("Event set by {}".format(threading.current_thread().name))
    if not e.is_set(): 
      e.set()
    time.sleep(3)

def job():
  while 1:
    e.wait()
    time.sleep(4)
    print("Event set?", e.is_set())
    e.clear()
    print("Event cleared by {}".format(threading.current_thread().name), "\n")

e = threading.Event()

t1 = threading.Thread(target=sleeper, name = "Thread {}".format(1))
t2 = threading.Thread(target=job, name = "Thread {}".format(2))
t1.start()
t2.start()
t1.join()
t2.join()
print("End")


