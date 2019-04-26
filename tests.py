import math
import numpy as np
import time

t = [1, 2, 3, 4, 5]
data = [1, 2, 7, 15, 50]
d = np.diff([t, data], axis=0)
print(d)