import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from common.defs import *
from common.serialUtility import *
from common.sample import *
from task.task import Task_Read
from queue import Queue
from threading import Thread
from sklearn.externals import joblib
import numpy as np


READ_TIMEOUT = 5
IDLE_SIZE = 2 * WINDOW_SIZE


def genWindow(raw:list):
    use = raw[-WINDOW_SIZE:]
    spl = [Sample(vals=da) for da in use]
    return Window(spl)

def genFeature(win:Window):
    res = []
    for i in range(ADC_NUM):
        res.append(win.range(i))
        res.append(win.std(i))
    res = np.array(res)
    return res


# ----------------------------------------
# init, discard init data

print("Initializing...")

clf = joblib.load(MODEL_DIR + "idleKNN.pkl")

q_read = Queue()
readTask = Task_Read([q_read])
t_read = Thread(target=readTask.run, name="thread_read")
t_read.start()

# subroutine for control
def control():
    while True:
        key = input()
        if len(key) < 1:
            continue
        if key[0] == 'q':
            readTask.terminate()
            print("Terminated!")
            exit(0)
        elif key[0] == 'p':
            print("Paused! Press 'r' to resume")
            readTask.pause()
        elif key[0] == 'r':
            print("Resumed. Logging...")
            readTask.resume()

# filter for initial data
for i in range(10):
    q_read.get(timeout=READ_TIMEOUT)

while True:
    print("Press 's' to collect data in idle state; press 'q' to quit")
    key = input()
    if key[0] == 's':
        print("Starting...")
        c_thread = Thread(target=control, name="thread_control")
        c_thread.start()
        break
    elif key[0] == 'q':
        readTask.terminate()
        exit(-2)

# -----------------------------------------------
# collect idle state data, calc mean & std

def windowAdd(window:list, data:list):
    for i in range(ADC_NUM):
        window.append(data)
    if len(window) > 2 * WINDOW_SIZE:
        window = window[-WINDOW_SIZE:]
    return window

rawWindow = []

print("Initializing first window...")
# collect first window
firstCnt = 0
while firstCnt < WINDOW_SIZE:
    vals = q_read.get()
    if vals:
        # print(vals)
        # vals = parseArray(vals)
        # print(vals)
        windowAdd(rawWindow, vals)
        firstCnt += 1

print("Predicting...")
lastPred = -1
processCnt = 0
stepCnt = 0
while True:
    if not t_read.is_alive():
        exit(-1)

    vals = q_read.get()
    if vals == None:
        continue
    # vals = parseArray(vals)
    windowAdd(rawWindow, vals)
    stepCnt += 1
    if stepCnt % 5 == 0:
        win = genWindow(rawWindow)
        feed = genFeature(win)
        y = clf.predict([feed])
        if y[-1] != lastPred:
            lastPred = y[-1]
            print("Predict: %s" % ('idle' if y[-1] == 0 else 'click'))

    # keep running sign
    tp = processCnt % 4
    if tp == 0:
        print('-', end='\r')
    elif tp == 1:
        print('\\', end='\r')
    elif tp == 2:
        print('|', end='\r')
    else:
        print('/', end='\r')
    processCnt += 1
    