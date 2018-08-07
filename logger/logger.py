import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)

import sys, time, os
from queue import Queue
from threading import Thread
import matplotlib.pyplot as plt
import numpy as np
from serialUtility import initSerial, readline, writeline
from task import Task

PORT_NAME = "COM4"
LOG_PATH = "../data/"

SENSOR_NUM = 6
PLOT_RANGE = 200
ARDU_DELAY = 0.05
PLOT_RATE = 1 / ARDU_DELAY / 2

class Task_Read(Task):
    def __init__(self, queues:list):
        super().__init__()
        self._out_queues = queues

    def _parseLine(self, line):
        line = line.strip()
        if line == '':
            return None
        vals = line.split(' ')
        if len(vals) < SENSOR_NUM:
            return None
        else:
            neo_vals = [int(val) for val in vals]
            return neo_vals
    
    # override
    def _enter(self):
        self._serial = initSerial(PORT_NAME)

    # override
    def _func(self):
        line = readline(self._serial)
        vals = self._parseLine(line)
        if vals:
            for queue in self._out_queues:
                queue.put_nowait(vals)

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
        vals = self._in_queue.get()
        line = " " + ' '.join('%d' % n for n in vals)
        self._fout.write(str(time.time()) + line + '\n')

# ! deprecated
class Task_Plot(Task):
    def __init__(self, queue:Queue):
        super().__init__()
        self._in_queue = queue
        self._time = []
        self._t_now = 0
        self._data = []
        for i in range(SENSOR_NUM):
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
        time.sleep(ARDU_DELAY)

# -----------------
class Logger:
    def __init__(self):
        self._started = False
        self.m_time = []
        self.data = []
        for i in range(PLOT_RANGE):
            self.data.append([])

    def _draw(self, t_arr, v_arr):
        plt.cla()
        self.m_time.extend(t_arr)
        # print(v_arr)
        for i in range(SENSOR_NUM):
            self.data[i].extend(v_arr[i])

        if len(self.m_time) > PLOT_RANGE:
            self.m_time = self.m_time[-PLOT_RANGE:]
            for i in range(SENSOR_NUM):
                self.data[i] = self.data[i][-PLOT_RANGE:]
        plt.xlim(self.m_time[-1] - PLOT_RANGE * ARDU_DELAY, self.m_time[-1] + ARDU_DELAY)

        colorStr = "rgbcmy"
        for i in range(SENSOR_NUM):
            plt.plot(self.m_time, self.data[i], '-'+colorStr[i])
        plt.pause(0.1)

    def start(self, filename, no):
        print("Press 's' to start logging")
        q_log = Queue()
        q_plt = Queue()

        readTask = Task_Read([q_log, q_plt])

        if not os.path.isdir(LOG_PATH + filename):
            os.mkdir(LOG_PATH + filename)

        if not os.path.isdir(LOG_PATH + filename + "/" + no):
            os.mkdir(LOG_PATH + filename + "/" + no)

        writeTask = Task_Log(q_log, filename=LOG_PATH + filename + "/" + no + '/' + "clay.txt")
        plotTask = Task_Plot(q_plt)
        
        t_read = Thread(target=readTask.run, name="thread_read")
        t_write = Thread(target=writeTask.run, name="thread_write")

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
        
        plotWindow = 50
        curWindowLen = 0
        curPos = 0
        plt.ion()
        # ax = plt.subplot()

        t_now = 0
        m_time = []
        data = []
        for i in range(SENSOR_NUM):
            data.append([])

        cnt = 0
        while self._started:
            vals = q_plt.get()
            cnt += 1
            m_time.append(t_now)
            for i in range(SENSOR_NUM):
                data[i].append(vals[i])
            t_now += ARDU_DELAY

            # if len(m_time) > PLOT_RANGE:
            #     m_time = m_time[-PLOT_RANGE:]
            #     for i in range(SENSOR_NUM):
            #         data[i] = data[i][-PLOT_RANGE:]
            # plt.xlim(m_time[-1] - PLOT_RANGE * ARDU_DELAY, m_time[-1] + ARDU_DELAY)

            # for i in range(SENSOR_NUM):
            #     plt.plot(m_time, data[i], '-'+colorStr[i])
            # print(cnt)
            if cnt % PLOT_RATE == 0:
                # print("draw")
                self._draw(m_time, data)
                m_time = []
                data = []
                for i in range(SENSOR_NUM):
                    data.append([])
                # cnt = 0
                # plt.cla()
                # plt.show()
            # if curWindowLen < plotWindow:
            #     if curPos % 10 == 0:
            #         # plt.cla()
            #         for i in range(SENSOR_NUM):
            #             plt.plot(m_time, data[i], '-'+colorStr[i])
            #     curWindowLen += 1
            # else:
            #     if curPos % 10 == 0:
            #         # plt.cla()
            #         for i in range(SENSOR_NUM):
            #             plt.plot(m_time[curPos-plotWindow:curPos], data[i][curPos-plotWindow:curPos], '-'+colorStr[i])
            # # ax.plot(y2,label='test')
            # # plt.legend(loc='best')
            # curPos += 1
            # plt.pause(0.01)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: %s output_filename port_no" % sys.argv[0])
        exit(-1)
    log = Logger() 
    log.start(sys.argv[1], sys.argv[2])
