import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from common.defs import *
import os.path
import time
from ctypes import c_double, cdll

import numpy as np
import serial

def read_data(data, offset):
    arr = []
    for i in range(3):
        arr.append(int(data[i * 2 + offset] << 8 | data[i * 2 + 1 + offset]))
        if arr[i] >= 2 ** 15:
            arr[i] -= 2 ** 16
    return arr

def read_data1(data, offset):
    return int(data[offset] << 8 | data[1 + offset])


# ----

dirname = sys.argv[1]
no = sys.argv[2]

if not os.path.isdir(DATA_DIR + dirname):
    os.mkdir(DATA_DIR + dirname)

if not os.path.isdir(DATA_DIR + dirname + "/" + no):
    os.mkdir(DATA_DIR + dirname + "/" + no)

ser = serial.Serial('COM6', 115200)
raw_datafile = open(DATA_DIR + dirname + "/" + no + '/' + 'press.txt', 'w')
ser.write(b'\x01')

count = 0

while True:
    # read data
    data = ser.read(16)
    weight = read_data1(data, 14)
    raw_datafile.write(str(time.time()) + ' ' + str(weight) + '\n')
    count += 1
    if count % 250 == 0:
        count = 0
        print(str(weight), end='\r')

'''
连线
模块 -> 开发板
VCC     3.3
GND     G
SCLK    A5
SDI     A7
SDO     A6
INT     A1
NCS     A4

AO      A2
VCC     3,3
GND     GND

'''
