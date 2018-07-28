import sys
from task import Task
from threading import Thread
from queue import Queue

from utility import initSerial, readline, writeline

PORT_NAME = "COM3"
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

# -----------------

def start(filename):
    print("Press 's' to start logging")
    q_log = Queue()
    readTask = Task_Read([q_log])
    writeTask = Task_Log(q_log, filename=LOG_PATH + filename + ".txt")
    t_read = Thread(target=readTask.run, name="thread_read")
    t_write = Thread(target=writeTask.run, name="thread_write")

    started = False
    while True:
        key = input()
        if key[0] == 's' and not started:
            print("Press 'q' to quit, 'p' to pause")
            print("Logging...")
            t_read.start()
            t_write.start()
            started = True
        elif key[0] == 'q':
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
