import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from common.defs import *
from common.serialUtility import *
from queue import Queue

import time

class Task:
    def __init__(self):
        self.__running = False
        self.__paused = False

    def isRunning(self):
        return self.__running

    def isPaused(self):
        return self.__paused

    def terminate(self):
        self.__running = False
    
    # blocked
    def pause(self):
        self.__paused = True

    def resume(self):
        self.__paused = False

    def run(self):
        if self.__running:
            return
        self.__running = True
        self._enter()

        # spin
        while self.isRunning():
            # spin
            while self.isPaused():
                if not self.isRunning():
                    break
            self._func()

        self._exit()
        self.__running = False
    
    # Override this function as the main function of task
    def _func(self):
        pass

    # Override this function as enter
    def _enter(self):
        pass

    # Override this function as exit
    def _exit(self):
        pass

# ----------------------------------------

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
