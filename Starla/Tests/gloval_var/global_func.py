import threading
import sys
import time
import queue

e = threading.Event()
e.set()
print(e.is_set())
time.sleep(10)
e.clear()

