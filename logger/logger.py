import sys, time
from queue import Queue
from threading import Thread
import matplotlib.pyplot as plt
import numpy as np

from task import Task
from utility import initSerial, readline, writeline

PORT_NAME = "COM5"
LOG_PATH = "../data/"

class Task_Read(Task):
    def __init__(self, queues:list):
        super().__init__()
        self._out_queues = queues
    
    # override
    def _enter(self):
        self._serial = initSerial(PORT_NAME)

    # override
    def _func(self):
        line = readline(self._serial)
        for queue in self._out_queues:
            queue.put_nowait(line)

class Task_Log(Task):
    def __init__(self, queue:Queue, filename):
        super().__init__()
        self._in_queue = queue
        self._filename = filename

    # override
    def _enter(self):
        self._fout = open(self._filename, 'w', encoding='utf-8')

    # override
    def _exit(self):
        if not self._fout.closed:
            self._fout.close()
    
    # override
    def _func(self):
        line = self._in_queue.get()
        self._fout.write(line + '\n')

class Task_Plot(Task):
    def __init__(self, queue:Queue):
        super().__init__()
        self._in_queue = queue
        self._time = []
        self._t_now = 0
        self._data = []
        for i in range(6):
            self._data.append([])

    # override
    def _enter(self):
        plt.ion()
        plt.figure(1)
        
    # override
    def _exit(self):
        pass
    
    # override
    def _func(self):
        line = self._in_queue.get()
        if line == '':
            return
        vals = line.split(' ')
        self._time.append(self._t_now)
        self._data[0].append(int(vals[0]))
        plt.plot(self._time, self._data[0], '-b')
        plt.draw()
        time.sleep(0.05)

# -----------------

def start(filename):
    print("Press 's' to start logging")
    q_log = Queue()
    q_plt = Queue()

    readTask = Task_Read([q_log, q_plt])
    writeTask = Task_Log(q_log, filename=LOG_PATH + filename + ".txt")
    plotTask = Task_Plot(q_plt)
    
    t_read = Thread(target=readTask.run, name="thread_read")
    t_write = Thread(target=writeTask.run, name="thread_write")
    t_plot = Thread(target=plotTask.run, name="thread_plot")

    started = False
    while True:
        key = input()
        if key[0] == 's' and not started:
            print("Press 'q' to quit, 'p' to pause")
            print("Logging...")
            t_read.start()
            t_write.start()
            t_plot.start()
            started = True
        elif key[0] == 'q':
            plotTask.terminate()
            writeTask.terminate()
            readTask.terminate()
            print("Terminated!")
            break
        elif key[0] == 'p':
            print("Paused!Press 'r' to resume")
            readTask.pause()
        elif key[0] == 'r':
            print("Resumed. Logging...")
            readTask.resume()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s output_filename" % sys.argv[0])
        exit(-1)
    start(sys.argv[1])
