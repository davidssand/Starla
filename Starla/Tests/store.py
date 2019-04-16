import time
import numpy as np
import pandas as pd

data = {"time":  [],
        "altitude": [],
        "pitch": []}

df = pd.DataFrame({"time":  [],
        "altitude": [],
        "pitch": []})

df.to_csv(r'data.csv')

data = {"time":  [10, 20, 30, 40],
        "altitude": [3, 20, 70, 123],
        "pitch": [20, 25, 30, 30]}

df = pd.DataFrame(data)

df.to_csv('data.csv', mode='a', header=False)

data = {"time":  [1234, 1234, 241],
        "altitude": [123, 0, 43],
        "pitch": [1213, 55, 67]}

df = pd.DataFrame(data)

df.to_csv('data.csv', mode='a', header=False)
