import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from common.defs import *
from common.utility import *
from common.sample import Sample

from matplotlib import pyplot as plt
import numpy as np

WINDOW_SIZE = 20
PRESS_THRESHOLD = 3000
DELTA_STD = 1e-4

def splitLine(line):
    line = line.strip()
    if line == '':
        return None
    vals = line.split(' ')
    if len(vals) < 1 + SENSOR_NUM:  # '1' for tp
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

        # set label
        if pre[1] <= PRESS_THRESHOLD:
            samples[cursor].label = no
        else:
            samples[cursor].label = -1
        validSamples.append(samples[cursor])
        cursor += 1
    
    pressed = False
    pressedCnt = 0
    for va in validSamples:
        if va.label == -1:
            if pressed:
                pressed = not pressed
        else:
            if not pressed:
                pressed = not pressed
                pressedCnt += 1
    print("In file '%s_%s', valid samples: %d, pressed points: %d" % (filename, no, len(validSamples), pressedCnt))
    return validSamples

# ---------------------------------------------------------------------

def filter_local(data:list):
    sorted(data, key=lambda x : x['tp'])
    res = []
    for i in range(WINDOW_SIZE, len(data)):
        mean = []
        std = []
        curLi = data[i - WINDOW_SIZE:i]
        for j in range(ADC_NUM):
            mean.append(np.mean([sp['data'][j] for sp in curLi]))
            std.append(np.std([sp['data'][j] for sp in curLi]))
        point = {}
        point['label'] = data[i]['label']
        point['tp'] = data[i]['tp']
        point['raw'] = data[i]['data']
        point['data'] = []
        for j in range(ADC_NUM):
            dividor = std[j] if std[j] != 0 else DELTA_STD
            point['data'].append((data[i]['data'][j] - mean[j]) / dividor)
        for j in range(ADC_NUM, SENSOR_NUM):
            point['data'].append(data[i]['data'][j] - data[i - 1]['data'][j])
        res.append(point)
    return res


if __name__ == '__main__':
    data = []

    for i in range(CLASS_NUM):
        print("Extracting %s_%d" % (sys.argv[1], i))
        samples = extract(sys.argv[1], i)
        data.extend([spl.__dict__ for spl in samples])
    print("")

    print("raw data len: %d" % len(data))
    print(data[-1])
    data = filter_local(data)
    print(data[-1])
    print("normalized data len: %d" % len(data))
    json_dump(data, sys.argv[1])
