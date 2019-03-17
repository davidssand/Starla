import threading

class Threader(threading.Thread):
    def __init__(self, name, target_function, daemon = None):
        threading.Thread.__init__(self, target=target_function, name = name, daemon = daemon)
        print('Thread de ' + name + ' iniciada')
        self.start()
