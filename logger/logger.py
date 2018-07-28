import sys, time
from queue import Queue
from threading import Thread
import matplotlib.pyplot as plt
import numpy as np

from task import Task
from utility import initSerial, readline, writeline

from math import *

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
class Logger:
    def __init__(self):
        self._started = False

    def start(self, filename):
        print("Press 's' to start logging")
        q_log = Queue()
        q_plt = Queue()

        readTask = Task_Read([q_log, q_plt])
        writeTask = Task_Log(q_log, filename=LOG_PATH + filename + ".txt")
        plotTask = Task_Plot(q_plt)
        
        t_read = Thread(target=readTask.run, name="thread_read")
        t_write = Thread(target=writeTask.run, name="thread_write")

        m_time = []
        t_now = 0
        data = []
        for i in range(6):
            data.append([])

        # fig,ax=plt.subplots()
        plt.ion()
        y1=[]
        y2=[]
        # plt.ion()
        # plt.figure(1)

        # subroutine for control
        def control():
            while True:
                key = input()
                if key[0] == 'q':
                    plotTask.terminate()
                    writeTask.terminate()
                    readTask.terminate()
                    self._started = False
                    print("Terminated!")
                    return
                elif key[0] == 'p':
                    print("Paused! Press 'r' to resume")
                    readTask.pause()
                elif key[0] == 'r':
                    print("Resumed. Logging...")
                    readTask.resume()

        # wait for user to start
        while True:
            key = input()
            if key[0] == 's':
                print("Press 'q' to quit, 'p' to pause")
                print("Logging...")
                self._started = True
                t_read.start()
                t_write.start()
                # t_plot.start()

                # new thread to control
                t_ctrl = Thread(target=control, name="thread_control")
                t_ctrl.start()
                break
        
        # start to draw
        

        while self._started:
            line = q_plt.get()
            if line == '':
                continue
            vals = line.split(' ')
            m_time.append(t_now)
            data[0].append(vals[0])
            t_now += 0.1
            # ax.cla()
            # ax.set_title("Loss")
            # ax.set_xlabel("Iteration")
            # ax.set_ylabel("Loss")
            # ax.set_xlim(0,55)
            # ax.set_ylim(0, 300)
            # ax.grid()
            plt.plot(m_time, data[0], label='train')
            # ax.plot(y2,label='test')
            # ax.legend(loc='best')
            plt.pause(0.1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s output_filename" % sys.argv[0])
        exit(-1)
    log = Logger() 
    log.start(sys.argv[1])
