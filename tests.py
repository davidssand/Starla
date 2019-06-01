import threading
import sys
import time
import queue
import numpy as np
import pandas as pd
import operator
import math
import random
import matplotlib.pyplot as plt

class Tester():
  def __init__(self):
    length = 5

    # ---------------------------- #
    # Long rm
    self.rm_lenght = length
    self.rm_sum = 0
    self.rm_input_index = 0
    self.rm_result = [random.randint(0, 10) for _ in range(0, self.rm_lenght)]
    for i in self.rm_result:
      self.rm_sum += i

    # ---------------------------- #
    # Short rm
    self.n = length
    self.mean = 5
    for i in range(0, length):
      self.short_rm(random.randint(0, 10))

  def long_rm(self, data):
    # --------------- #

    # Running mean for velocity

    # --------------- #
    self.rm_sum -= self.rm_result[self.rm_input_index]
    self.rm_result[self.rm_input_index] = data
    self.rm_sum += self.rm_result[self.rm_input_index]
    self.rm_input_index = (self.rm_input_index + 1) % self.rm_lenght

    # print("result", self.rm_result)
    # print("input_index", self.rm_input_index)
    # print("sum", self.rm_sum)

    return self.rm_sum/self.rm_lenght

  def short_rm(self, data):
    self.mean = (self.mean * self.n + data)/(self.n + 1)
    return self.mean

read = [random.randint(0, 10) for i in range(0, 1000)]

tester = Tester()

# Long running mean
long_f = []

# Short running mean
short_f = []

for i in read:
  long_f.append(tester.long_rm(i))

# -------

for i in read:
  short_f.append(tester.short_rm(i))

plt.plot(long_f)
plt.legend("long")

plt.plot(short_f)
plt.legend("short")

# plt.plot(read)
# plt.ylabel('raw')

plt.show()
# -----------