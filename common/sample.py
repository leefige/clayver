import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)

from defs import *

class Sample:
    def __init__(self, tp:int, vals:list):
        self.tp = tp
        self.label = -1
        self.data = []
        assert len(vals) == SENSOR_NUM
        for i in range(SENSOR_NUM):
            self.data.append(vals[i])
    
    def __getitem__(self, index:int):
        assert index >= 0
        return self.data[index]

