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
from keras.models import load_model

READ_TIMEOUT = 5
IDLE_SIZE = 2 * WINDOW_SIZE
FEED_LEN = 10


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

# data: non-idle list
def genFeature_lstm_event(data:list):
    assert len(data) == FEED_LEN + 1
    mean = []
    std = []
    rang = []
    for i in range(ADC_NUM):
        tmpLi = [da[i] for da in data]
        mean.append(np.mean(tmpLi))
        std.append(np.std(tmpLi))
        rang.append(max(tmpLi) - min(tmpLi))

    feed = []
    for i in range(1, len(data)):
        res = genFeature_lstm_idle(data[i])
        for j in range(ADC_NUM):
            res.append(std[j])
            res.append(rang[j])
            res.append(data[i][j] - data[i-1][j])
            res.append(data[i][j] - mean[j])
        assert len(res) == ADC_NUM * 7
        feed.append(res)
    assert len(feed) == FEED_LEN
    # if data[-1].label == -1:
    #     print(data[-1].label)
    return feed

def genFeature_lstm_idle(spl:Sample):
    # get idle data
    idleMean = []
    idleStd = []
    idleRange = []
    for i in range(ADC_NUM):
        tmpLi = [idl[i] for idl in spl.relatedIdle]
        idleMean.append(np.mean(tmpLi))
        idleStd.append(np.std(tmpLi))
        idleRange.append(max(tmpLi) - min(tmpLi))
    
    # generate feature
    res = []
    for i in range(ADC_NUM):
        res.append(idleStd[i])
        res.append(idleRange[i])
        res.append(spl[i] - idleMean[i])
    assert len(res) == ADC_NUM * 3
    return res

# data: non-idle list
def genFeature_lstm(data:list):
    assert len(data) == FEED_LEN + 1
    mean = []
    std = []
    rang = []
    for i in range(ADC_NUM):
        tmpLi = [da[i] for da in data]
        mean.append(np.mean(tmpLi))
        std.append(np.std(tmpLi))
        rang.append(max(tmpLi) - min(tmpLi))

    feed = []
    for i in range(1, len(data)):
        res = genFeature_lstm_idle(data[i])
        for j in range(ADC_NUM):
            res.append(std[j])
            res.append(rang[j])
            res.append(data[i][j] - data[i-1][j])
            res.append(data[i][j] - mean[j])
        assert len(res) == ADC_NUM * 7
        feed.append(res)
    assert len(feed) == FEED_LEN
    # if data[-1].label == -1:
    #     print(data[-1].label)
    return feed

# ----------------------------------------
# init, discard init data
class_num = CLASS_NUM
print("Initializing...")

clf = joblib.load(MODEL_DIR + "idleKNN.pkl")
lstm = load_model(MODEL_DIR + "lstm_%d.hdf5" % class_num)
lstm_event = load_model(MODEL_DIR + "lstm_2.hdf5")

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
curIdle = genWindow(rawWindow).samples[-(FEED_LEN+1):]
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
        y_event = y[-1]

# -------
        # samples = win.samples[-(FEED_LEN+1):]
        # for sp in samples:
        #     sp.setRelated(curIdle)
        # feed = genFeature_lstm(samples)
        # # print(feed)
        # X = np.array([feed])
        # y = lstm_event.predict(X)
        # y_event = np.argmax(y[-1])
# --------

        if y_event == 0:
            curIdle = win.samples[-(FEED_LEN+1):]
        if y_event != lastPred:
            samples = win.samples[-(FEED_LEN+1):]
            for sp in samples:
                sp.setRelated(curIdle)
            feed = genFeature_lstm(samples)
            # print(feed)
            X = np.array([feed])
            y = lstm.predict(X)
            # re-estimate
            if np.argmax(y[-1]) == class_num:
                y_event = 0

            if y_event != lastPred:
                lastPred = y_event
                print("Predict: %s" % ('idle' if y_event == 0 else ('click\a` %d' % np.argmax(y[-1]))))

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
    