import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from common.defs import *
from common.utility import *
from common.sample import Sample

from matplotlib import pyplot as plt
import numpy as np

WINDOW_SIZE = 10
PRESS_THRESHOLD = 3000

SENSOR_NUM = 6
class Window:
    def __init__(self):
        self._MAX_SIZE = WINDOW_SIZE
        self.size = 0
        self._sum = [0 for i in range(SENSOR_NUM)]
        self._min = [(1 << 32) for i in range(SENSOR_NUM)]
        self._max = [-1 for i in range(SENSOR_NUM)]
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

        assert SENSOR_NUM == sample.getFeatLen()
        if self.size == 0:
            self.start = pos
        self.end = pos + 1
        self.size += 1
        for i in range(SENSOR_NUM):
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
    for i in range(SENSOR_NUM):
        idle_data.append([da[i] for da in idles])
    
    means = [np.mean(li) for li in idle_data]
    print(means)

    ranges = []
    mins = []
    stds = []
    flat_data = []
    for i in range(SENSOR_NUM):
        flat_data.append([])

    for key in data.keys():
        li = data[key]
        for i in range(SENSOR_NUM):
            flat_data[i].extend([da['data'][i] for da in li])

    for i in range(SENSOR_NUM):
        ranges.append(np.max(flat_data[i]) - np.min(flat_data[i]))
        mins.append(np.min(flat_data[i]))
        stds.append(np.std(flat_data[i]))
    print(ranges)
    print(mins)
    print(stds)

    for key in data.keys():
        li = data[key]
        for it in li:
            for i in range(SENSOR_NUM):
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
            pureData = [[]] * SENSOR_NUM

    return samples

def filter_local(data:dict):
    print(data.keys())
    idles = [da['data'] for da in data[-1]]
    idle_data = []
    for i in range(SENSOR_NUM):
        idle_data.append([da[i] for da in idles])
    
    means = [np.mean(li) for li in idle_data]
    print(means)

    ranges = []
    mins = []
    stds = []
    flat_data = []
    for i in range(SENSOR_NUM):
        flat_data.append([])

    for key in data.keys():
        li = data[key]
        for i in range(SENSOR_NUM):
            flat_data[i].extend([da['data'][i] for da in li])

    for i in range(SENSOR_NUM):
        ranges.append(np.max(flat_data[i]) - np.min(flat_data[i]))
        mins.append(np.min(flat_data[i]))
        stds.append(np.std(flat_data[i]))
    print(ranges)
    print(mins)
    print(stds)

    for key in data.keys():
        li = data[key]
        for it in li:
            for i in range(SENSOR_NUM):
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
        if cursor >= len(samples):
            break
        if pre[0] < samples[cursor].tp:
            continue
        elif pre[0] > samples[cursor].tp:
            cursor += 1
            continue
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

# use local extractor



if __name__ == '__main__':
    data = {}

    for i in range(-1, CLASS_NUM):
        data[i] = []
    for i in range(CLASS_NUM):
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
