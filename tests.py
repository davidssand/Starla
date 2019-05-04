import threading
import sys
import time
import queue
import numpy as np
import pandas as pd
import operator
import math

df2 = pd.DataFrame({"time": [1 for i in range(0, 10**(7))]})
df2.to_csv(r'data2.csv')

read2 = pd.read_csv('data2.csv')

print("read2" + " size", read2.memory_usage(index=True).sum())


