from threading import Thread
import threading
from queue import Queue
from typing import *
import types
import time

running = True
global_count = 10000
curr_count = 0

def download_pics(queue:Queue, lock:threading.Lock):
    global curr_count
    global global_count
    print("enter download_pics")
    while True:
        lock.acquire(timeout=1)
        if curr_count < global_count:
            dict_info = queue.get()
            print(dict_info['id'])
            curr_count += 1
            lock.release()
        else:
            lock.release()
            break

class Producer:
    def __init__(self, queue: Queue, lock:threading.Lock, handler:types.FunctionType=None):
        self._queue = queue
        self._lock = lock

    def produce(self, dict_info:Dict[str, any]):
        self._lock.acquire()
        self._queue.put(dict_info)
        self._lock.release()

threads = []
queue = Queue()
lock = threading.Lock()
producer = Producer(queue, lock)

for i in range(5):
    threads.append(Thread(target=download_pics, args=(queue, lock)))

for i in range(10000):
    producer.produce({'id':i})

for i in range(5):
    threads[i].start()

while True:
    lock.acquire()
    if curr_count == global_count:
        running = False
        for i in range(5):
            threads[i].join()
        lock.release()
        break
    lock.release()
    time.sleep(1)
