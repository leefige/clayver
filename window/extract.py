DATA_DIR = "../data/"
WINDOW_SIZE = 10
TOUCH_CNT = 5
FEAT_SIZE = 6

class Sample:
    def __init__(self, vals:list):
        self._FEAT_SIZE = FEAT_SIZE
        self._data = []
        assert len(vals) == self._FEAT_SIZE
        for i in range(self._FEAT_SIZE):
            self._data.append(vals[i])
    
    def __getitem__(self, index:int):
        assert index >= 0
        return self._data[index]

    def getFeatLen(self):
        return self._FEAT_SIZE
    
class Window:
    def __init__(self):
        self._FEAT_SIZE = FEAT_SIZE
        self._MAX_SIZE = WINDOW_SIZE
        self.size = 0
        self._sum = [0 for i in range(self._FEAT_SIZE)]
        self._min = [(1 << 32) for i in range(self._FEAT_SIZE)]
        self._max = [-1 for i in range(self._FEAT_SIZE)]
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

        assert self._FEAT_SIZE == sample.getFeatLen()
        if self.size == 0:
            self.start = pos
        self.end = pos + 1
        self.size += 1
        for i in range(self._FEAT_SIZE):
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
    if len(vals) < 6:
        return None
    else:
        neo_vals = [int(val) for val in vals]
        return neo_vals

def extract(filename):
    path = DATA_DIR + filename + ".txt"
    
    samples = []
    # extract samples from file
    with open(path, 'r', encoding='utf8') as fin:
        for line in fin:
            vals = splitLine(line)
            if vals:
                samples.append(Sample(vals))
    print("In file '%s', valid samples: %d" % (filename, len(samples)))
    pos = 0
    windows = []
    curWindow = Window()
    maxPos = len(samples)
    
    while True:
        cur = pos
        while cur < maxPos and curWindow.add(samples[cur], cur):
            cur += 1
        pos += 1
        windows.append(curWindow)
        # go on?
        if curWindow.end == maxPos:
            break
        else:
            curWindow = Window()

    for window in windows:
        print("(%d, %d): %d" % (window.start, window.end, window.getMean(0)))

    return windows

if __name__ == '__main__':
    extract("wsy_0")