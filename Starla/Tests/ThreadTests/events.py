import threading
import sys
import time
import queue

def sleeper():
  while 1:
    if not e.is_set(): 
      print("Event set by {}".format(threading.current_thread().name))
      e.set()

def job():
  while 1:
    e.wait()
    print("Event set?", e.is_set())
    time.sleep(2)
    e.clear()
    print("Event cleared by {}".format(threading.current_thread().name), "\n")

e = threading.Event()
f = threading.Event()

t1 = threading.Thread(target=sleeper, name = "Thread {}".format(1))
t2 = threading.Thread(target=job, name = "Thread {}".format(2))
t1.start()
t2.start()
t1.join()
t2.join()
print("End")


