import copy
class A():
  def __init__(self):
    self.b = 1
    print(self.b)
    self.c(self.b)
    print(self.b)
  
  def c(self, attr):
    a = copy.deepcopy(attr)
    a = 2
A()