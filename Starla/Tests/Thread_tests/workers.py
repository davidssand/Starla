import threading
import sys
import time
import queue

def sleeper(w):
  print("Thread {} sleeping".format(threading.current_thread().name), w)
  time.sleep(3)
  print("Thread {} woke up".format(threading.current_thread().name), w)

def job():
  while 1:
    w = q.get()
    sleeper(w)
    q.task_done()

def creator():
  for i in range(5):
    t = threading.Thread(target=job, name = "Thread {}".format(i), daemon = True)
    t.start()

e = threading.Event()
q = queue.Queue()

t0 = time.time()
creator()

for worker in range(5):
  q.put(worker)

q.join()
print("Took: ", time.time() - t0, "s")


