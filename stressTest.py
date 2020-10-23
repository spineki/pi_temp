import time
from multiprocessing import Pool


def stress_test(delta = 10): # default 10 seconds stress test
    startTime = time.perf_counter()
    while time.perf_counter()-startTime < delta:
        x = 10
        x**x

if __name__ == '__main__':
    t = 60 * 60
    pool = Pool(processes = 4)
    pool.map(stress_test, (t,t,t,t))
    pool.close()
    pool.join()

