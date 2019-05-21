# -*- coding: utf-8 -*-

import threading

class Threader(threading.Thread):
  def __init__(self, name, target):
    threading.Thread.__init__(self, name=name, target=target)
    self.start()
    self.kill_me = threading.Event()

  def stop(self):
    self.kill_me.set()

  def stopped(self):
    return self.kill_me.is_set()