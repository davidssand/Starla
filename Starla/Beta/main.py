import threading
import sys
import time
import queue
sys.path.append("/home/david/APEX/Starla/Starla")

from Managers.Thread import Threader

def b():
  while 1:
    time.sleep(1)
    print("hb")

bT = Threader("2", b())

q = queue.Queue()
for i in range(5):
  q.put(i)

while not q.empty():
  print(q.get())


