import threading
import sys
import time
import queue
import numpy as np
import pandas as pd

t0 = time.time()

def job():
  while 1:
    l = q.get()
    print("starting job")
    print(l["b"])
    print("job ended")

a = 25
q = queue.Queue()
t = threading.Thread(target = job, name = "Read and Decide", daemon=True)
t.start()

t0 = time.time()
while time.time() - t0 < 3:
  time.sleep(0.5)
  q.put({"a": [1, 2], "b": [6, 8]})

print(q.empty())





