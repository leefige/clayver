import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from common.defs import *
from common.serialUtility import *
from task.task import Task_Read
from queue import Queue
from threading import Thread
from sklearn.externals import joblib
import numpy as np

ADC_NUM = 6

READ_TIMEOUT = 5
IDLE_SIZE = 3 * WINDOW_SIZE

# init, discard init data

print("Initializing...")

clf = joblib.load(MODEL_DIR + "KNN.pkl")

q_read = Queue()
readTask = Task_Read([q_read])
t_read = Thread(target=readTask.run, name="thread_read")
t_read.start()

# filter for initial data
for i in range(2 * WINDOW_SIZE):
    q_read.get(timeout=READ_TIMEOUT)

while True:
    print("Press 's' to collect data in idle state; press 'q' to quit")
    key = input()
    if key[0] == 's':
        print("Starting...")
        break
    elif key[0] == 'q':
        readTask.terminate()
        exit(-2)

# -----------------------------------------------
# collect idle state data, calc mean & std

# window: [[], [], [], [], [], []]
# data: [x, x, x, x, x, x]
def windowAdd(window:list, data:list):
    for i in range(ADC_NUM):
        window[i].append(data[i])
    if len(window[0]) > 2 * WINDOW_SIZE:
        for i in range(ADC_NUM):
            window[i] = window[i][-WINDOW_SIZE:]
    return window

# print("Collecting idle data")
# idleWindow = [[]] * ADC_NUM
# idleCnt = 0
# while idleCnt < IDLE_SIZE:
#     vals = q_read.get()
#     if vals:
#         windowAdd(idleWindow, vals)
#         idleCnt += 1

# print("Calculating idle data")
# mean_glob = []
# std_glob = []
# for i in range(ADC_NUM):
#     mean_glob.append(np.mean(idleWindow[i]))
#     std_glob.append(np.std(idleWindow[i]))
# print("mean & std:")
# print(mean_glob)
# print(std_glob)

# --------------------------------------------
# start to predict

# def parseArray(arr:list):
#     global mean_glob
#     global std_glob
#     for i in range(ADC_NUM):
#         arr[i] = (arr[i] - mean_glob[i]) / std_glob[i]
#     return arr

window = [[]] * ADC_NUM

print("Initializing first window...")
# collect first window
firstCnt = 0
while firstCnt < WINDOW_SIZE:
    vals = q_read.get()
    if vals:
        # print(vals)
        # vals = parseArray(vals)
        # print(vals)
        windowAdd(window, vals)
        firstCnt += 1

def dataFilter(window:list, targ:int):
    mean = []
    std = []
    for j in range(ADC_NUM):
        mean.append(np.mean(window[j][targ - WINDOW_SIZE:targ]))
        std.append(np.std(window[j][targ - WINDOW_SIZE:targ]))
    point = []
    for j in range(ADC_NUM):
        dividor = std[j] if std[j] != 0 else 1e-4
        point.append((window[j][targ] - mean[j]) / dividor)
    res = np.array([point])
    return res

# predict process
# [[], [], [], [], [], []] => [[x, x, x, x, x, x], [x, x, x, x, x, x], ...]
def genFeature(window:list):
    res = []
    for i in range(WINDOW_SIZE):
        # * assert i < WINDOW_SIZE
        res.append([window[j][i - WINDOW_SIZE] for j in range(ADC_NUM)])
    res = np.array(res)
    assert res.shape == (WINDOW_SIZE, ADC_NUM)
    return res

print("Predicting...")
lastPred = -1
processCnt = 0
while True:
    vals = q_read.get()
    if vals == None:
        continue
    
    # vals = parseArray(vals)
    windowAdd(window, vals)
    feed = dataFilter(window, -1)
    y = clf.predict(feed)
    # print(feed, end='\r')
    if y[-1] != lastPred:
        lastPred = y[-1]
        print("Predict: %d" % y[-1])
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