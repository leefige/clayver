import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

import time
from queue import Queue
from threading import Thread

import matplotlib.pyplot as plt
import numpy as np

from common.defs import *
from common.serialUtility import initSerial, readline, writeline
from task.task import Task_Log, Task_Read

SENSOR_NUM = 15
PLOT_RANGE = 200
PLOT_RATE = 10
# -----------------
class Logger:
    def __init__(self):
        self._DRAW_NUM = 6
        self._started = False
        self.m_time = []
        self.data = []
        for i in range(PLOT_RANGE):
            self.data.append([])

    def _draw(self, t_arr, v_arr):
        plt.cla()
        self.m_time.extend(t_arr)
        # print(v_arr)
        for i in range(self._DRAW_NUM):
            self.data[i].extend(v_arr[i])

        if len(self.m_time) > PLOT_RANGE:
            self.m_time = self.m_time[-PLOT_RANGE:]
            for i in range(self._DRAW_NUM):
                self.data[i] = self.data[i][-PLOT_RANGE:]
            plt.xlim(self.m_time[-1] - PLOT_RANGE * ARDU_DELAY, self.m_time[-1] + ARDU_DELAY)
        else:
            plt.xlim(0, PLOT_RANGE * ARDU_DELAY)

        colorStr = "rgbcmy"
        for i in range(self._DRAW_NUM):
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
        
        t_read = Thread(target=readTask.run, name="thread_read")
        t_write = Thread(target=writeTask.run, name="thread_write")

        # subroutine for control
        def control():
            while True:
                key = input()
                if len(key) < 1:
                    continue
                if key[0] == 'q':
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
            if len(key) < 1:
                continue
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
