from datetime import datetime
import time

def console_out(msg, error=False):
    if(error):
        print("[" + datetime.now().strftime('%H:%M:%S') + "]: ERROR-> " + msg)
    else:
        print("[" + datetime.now().strftime('%H:%M:%S') + "]: " + msg)

def tick():
    global stopwatch
    stopwatch = time.time()

def tock(msg=None):
    global stopwatch
    if(msg != None):
        print("T' [%s] = %.3f s" % (msg, time.time() - stopwatch))
    else:
        print("T' = %.3f s" % (time.time() - stopwatch))
    stopwatch = time.time()

def calc_temp(mV):
    d = [0.0e0,1.7057035e1,-2.3301759e-1,6.5435585e-3,-7.3562749e-5,-1.7896001e-6,8.4036165e-8,-1.3735879e-9,1.0629823e-11,-3.2447087e-14]
    temp = 0
    for i in range(len(d)):
        temp = temp+d[i]*mV**i
    return temp

def timeout(func, seconds):
    import multiprocessing
    p = multiprocessing.Process(target = func)
    p.start()
    p.join(seconds)
    if(p.is_alive()):
        p.terminate()
        p.join()
        raise ValueError("Timeout")

class Benchmark:
    def __init__(self):
        self.T = time.time()
        self.N = 0
        self.FPS = -1

    def mark(self):
        self.N += 1
        if(self.N > 10):
            try:
                self.FPS = self.N/(time.time()-self.T)
            except ZeroDivisionError: #if time difference is zero, leave frames per second as is
                pass
            self.T = time.time()
            self.N = 0
