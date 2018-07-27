import sys
from threading import Thread

from utility import initSerial, readline, writeline

PORT_NAME = "COM3"
LOG_PATH = "../data/"

class Task_Read:
    def __init__(self, dst_file):
        self._running = True
        self._paused = False
        self._dstFile = dst_file

    def terminate(self):
        self._running = False
    
    # blocked
    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def run(self):
        ser = initSerial(PORT_NAME)
        with open(self._dstFile, 'w', encoding='utf-8') as fout:
            while self._running:
                while self._paused:
                    pass
                line = readline(ser)
                fout.write(line + '\n')
                # print(line)

# -----------------

def start(filename):
    print("Press 's' to start logging")
    readTask = Task_Read(LOG_PATH + filename + ".txt")
    while True:
        key = input()
        if key[0] == 's':
            print("Press 'q' to quit, 'p' to pause")
            print("Logging...")
            t_read = Thread(target=readTask.run, name="thread_read")
            t_read.start()
        elif key[0] == 'q':
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
