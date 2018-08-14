import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)

from defs import *
import numpy as np

class Sample:
    def __init__(self, obj:dict=None, tp:int=None, vals:list=None):
        if obj == None:
            self.tp = tp
            self.label = -1
            self.data = []
            assert len(vals) == SENSOR_NUM
            for i in range(SENSOR_NUM):
                self.data.append(vals[i])
        else:
            self.tp = obj['tp']
            self.label = obj['label']
            self.data = obj['data']
    
    def __getitem__(self, index:int):
        assert index >= 0
        return self.data[index]

class Window:

    eventType = {'idle': 0, 'click': 1, 'press': 2}

    # li: list(Sample)
    def __init__(self, li:list=None):
        if li == None:
            self.samples = []
        else:
            assert len(li) > 0
            assert isinstance(li[0], Sample)
            self.samples = li
        self.pos = None
        self.event = None
        
    def add(self, pt:Sample):
        self.samples.append(pt)
    
    def decide(self):
        if self.pos == None:
            pos = -1
            for sp in self.samples:
                if sp.label != -1:
                    pos = sp.label
                    break
            self.pos = pos

        assert self.size() > 1
        if self.event == None:
            event = Window.eventType['idle']
            pos = self.samples[0].label
            if pos == -1:
                nonIdleCnt = 0
                for sp in self.samples[1:]:
                    if sp.label != -1:
                        nonIdleCnt += 1
                if nonIdleCnt > self.size() * 0.25:
                        event = Window.eventType['click']
            else:
                event = Window.eventType['press']
                idleCnt = 0
                for sp in self.samples[1:]:
                    if sp.label == -1:
                        idleCnt += 1
                if idleCnt > 0:
                    event = Window.eventType['idle']
            self.event = event
        return self.event

    def size(self):
        return len(self.samples)
    
    def mean(self, idx:int):
        return np.mean([sp[idx] for sp in self.samples])
    
    def max(self, idx:int):
        # print(self.samples[0])
        return max([sp[idx] for sp in self.samples])

    def min(self, idx:int):
        return min([sp[idx] for sp in self.samples])
    
    def range(self, idx:int):
        return self.max(idx) - self.min(idx)
    
    def std(self, idx:int):
        return np.std([sp[idx] for sp in self.samples])

class IdleState:
    def __init__(self, idle:Window):
        self.mean = [idle.mean(i) for i in range(SENSOR_NUM)]
        self.max = [idle.max(i) for i in range(SENSOR_NUM)]
        self.min = [idle.min(i) for i in range(SENSOR_NUM)]
        self.range = [(self.max[i] - self.min[i]) for i in range(SENSOR_NUM)]
        self.std = [idle.std(i) for i in range(SENSOR_NUM)]