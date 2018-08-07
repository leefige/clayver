from matplotlib import pyplot as plt
import sys
import json
import numpy as np
from utility import *
from json import JSONEncoder

DATA_DIR = "../data/"
WINDOW_SIZE = 10
TOUCH_CNT = 5

PRESS_THRESHOLD = 3000

class Sample:
    def __init__(self, tp:int, vals:list):
        self.tp = tp
        self.label = -1
        self.data = []
        assert len(vals) == FEAT_SIZE
        for i in range(FEAT_SIZE):
            self.data.append(vals[i])
    
    def __getitem__(self, index:int):
        assert index >= 0
        return self.data[index]
    
class Window:
    def __init__(self):
        self._MAX_SIZE = WINDOW_SIZE
        self.size = 0
        self._sum = [0 for i in range(FEAT_SIZE)]
        self._min = [(1 << 32) for i in range(FEAT_SIZE)]
        self._max = [-1 for i in range(FEAT_SIZE)]
        self.start = 0
        self.end = 0

    def getMax(self, i:int):
        return self._max[i]

    def getMin(self, i:int):
        return self._min[i]

    def getSum(self, i:int):
        return self._sum[i]

    def getSize(self):
        return self.size
    
    def getMean(self, i:int):
        return self._sum[i] / self.size
    
    def add(self, sample:Sample, pos:int):
        if self.size >= self._MAX_SIZE:
            return False

        assert FEAT_SIZE == sample.getFeatLen()
        if self.size == 0:
            self.start = pos
        self.end = pos + 1
        self.size += 1
        for i in range(FEAT_SIZE):
            if self._max[i] < sample[i]:
                self._max[i] = sample[i]
            if self._min[i] > sample[i]:
                self._min[i] = sample[i]
            self._sum[i] += sample[i]
        return True

def splitLine(line):
    line = line.strip()
    if line == '':
        return None
    vals = line.split(' ')
    if len(vals) < 7:
        return None
    else:
        tp = round(float(vals[0]) * 1000)
        neo_vals = [int(val) for val in vals[1:]]
        return tp, neo_vals

def filter(data:dict):
    print(data.keys())
    idles = [da['data'] for da in data[-1]]
    idle_data = []
    for i in range(FEAT_SIZE):
        idle_data.append([da[i] for da in idles])
    
    means = [np.mean(li) for li in idle_data]
    print(means)

    ranges = []
    mins = []
    stds = []
    flat_data = []
    for i in range(FEAT_SIZE):
        flat_data.append([])

    for key in data.keys():
        li = data[key]
        for i in range(FEAT_SIZE):
            flat_data[i].extend([da['data'][i] for da in li])

    for i in range(FEAT_SIZE):
        ranges.append(np.max(flat_data[i]) - np.min(flat_data[i]))
        mins.append(np.min(flat_data[i]))
        stds.append(np.std(flat_data[i]))
    print(ranges)
    print(mins)
    print(stds)

    for key in data.keys():
        li = data[key]
        for it in li:
            for i in range(FEAT_SIZE):
                # it['data'][i] = (it['data'][i] - means[i]) / ranges[i]
                it['data'][i] = (it['data'][i] - means[i]) / stds[i]
    # print(data)
    return data

def parseLocal(samples:list, window_size:int):
    for i in range(len(samples)):
        if i == 0:
            pass
        if i < window_size:
            window = i
        else:
            window = window_size
        localRange = samples[i - window:i]
        for item in samples[i - window:i]:
            pureData = [[]] * FEAT_SIZE

    return samples

def filter_local(data:dict):
    print(data.keys())
    idles = [da['data'] for da in data[-1]]
    idle_data = []
    for i in range(FEAT_SIZE):
        idle_data.append([da[i] for da in idles])
    
    means = [np.mean(li) for li in idle_data]
    print(means)

    ranges = []
    mins = []
    stds = []
    flat_data = []
    for i in range(FEAT_SIZE):
        flat_data.append([])

    for key in data.keys():
        li = data[key]
        for i in range(FEAT_SIZE):
            flat_data[i].extend([da['data'][i] for da in li])

    for i in range(FEAT_SIZE):
        ranges.append(np.max(flat_data[i]) - np.min(flat_data[i]))
        mins.append(np.min(flat_data[i]))
        stds.append(np.std(flat_data[i]))
    print(ranges)
    print(mins)
    print(stds)

    for key in data.keys():
        li = data[key]
        for it in li:
            for i in range(FEAT_SIZE):
                # it['data'][i] = (it['data'][i] - means[i]) / ranges[i]
                it['data'][i] = (it['data'][i] - means[i]) / stds[i]
    # print(data)
    return data

def extract(filename:str, no:int):
    path = DATA_DIR + filename + "/" + str(no) + "/clay.txt"
    pressPath = DATA_DIR + filename  + "/" + str(no) + "/press.txt"
    
    samples = []
    # extract samples from file
    with open(path, 'r', encoding='utf8') as fin:
        for line in fin:
            tp, vals = splitLine(line)
            if vals:
                samples.append(Sample(tp, vals))
    
    presses = []
    with open(pressPath, 'r', encoding='utf8') as fin:
        for line in fin:
            vals = line.split(' ')
            presses.append([round(float(vals[0]) * 1000), int(vals[1])])

    # annotation
    cursor = 0
    validSamples = []
    for pre in presses:
        if cursor == len(samples):
            break
        if pre[0] < samples[cursor].tp:
            continue
        elif pre[0] > samples[cursor].tp:
            cursor += 1
        if pre[1] <= PRESS_THRESHOLD:
            samples[cursor].label = no
        else:
            samples[cursor].label = -1
        validSamples.append(samples[cursor])
        cursor += 1
    
    print("In file '%s_%s', valid samples: %d" % (filename, no, len(validSamples)))
    for va in validSamples:
        if va.label == -1:
            print(" ", end='')
        else:
            print(va.label, end='')


    # * Show raw samples here
    # for i in range(0, 6):
    #     plt.subplot(2, 3, i+1)
    #     mi = []
    #     ma = []
    #     me = []
    #     idx = []
    #     cur = 0
    #     for win in samples:
    #         idx.append(cur)
    #         cur += 1
    #         mi.append(win[i])
    #     plt.title(filename)
    #     plt.plot(idx, mi, "-r")
        # plt.plot(idx, ma, "--b")
        # plt.plot(idx, me, ".-g")

    # plt.show()
    
    # ! no use, window
    # pos = 0
    # windows = []
    # curWindow = Window()
    # maxPos = len(samples)
    
    # while True:
    #     cur = pos
    #     while cur < maxPos and curWindow.add(samples[cur], cur):
    #         cur += 1
    #     pos += 1
    #     windows.append(curWindow)
    #     # go on?
    #     if curWindow.end == maxPos:
    #         break
    #     else:
    #         curWindow = Window()
    # return windows
    return validSamples

if __name__ == '__main__':
    data = {}

    for i in range(-1, FEAT_SIZE):
        data[i] = []
    for i in range(FEAT_SIZE):
        print("Extracting %s_%d" % (sys.argv[1], i))
        samples = extract(sys.argv[1], i)
        for sample in samples:
            obj = sample.__dict__
            del obj['tp']
            data[sample.label].append(obj)
    
    data_ = filter(data)
    # print(data_)
    json_dump(data, sys.argv[1])

    # for window in windows:
    #     print("(%d, %d): %d" % (window.start, window.end, window.getMean(0)))
