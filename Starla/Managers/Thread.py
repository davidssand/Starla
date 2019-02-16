import threading


class Thread(threading.Thread):
    def __init__(self, name, target_function, delay):
        threading.Thread.__init__(self, target=target_function, args=(delay,))
        print('Thread de ' + name + ' iniciada')
        self.start()
