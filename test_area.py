import time
import threading

def test_thread1(lock):
    while True:
        lock.acquire()
        print("number 1")
        lock.release()
        time.sleep(1)

def test_thread2(lock):
    while True:
        lock.acquire()
        print("number 2")
        lock.release()
        time.sleep(1)

if __name__ == "__main__":
    locks = [threading.Lock(), threading.Lock()]
    t1 = threading.Thread(target = test_thread1, args=(locks[0],))
    t2 = threading.Thread(target = test_thread2, args=(locks[1],))
    t1.start()
    t2.start()
    locks[1].acquire()
    while True:
        print("main")
  
        time.sleep(3)