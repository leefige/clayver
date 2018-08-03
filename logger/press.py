import datetime
import time, sys, os.path

import serial

import numpy as np

from ctypes import cdll
from ctypes import c_double

DATA_PATH = "../data/"

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

if not os.path.isdir(DATA_PATH + dirname):
    os.mkdir(DATA_PATH + dirname)

if not os.path.isdir(DATA_PATH + dirname + "/" + no):
    os.mkdir(DATA_PATH + dirname + "/" + no)

ser = serial.Serial('COM6', 115200)
raw_datafile = open(DATA_PATH + dirname + "/" + no + '/' + 'press.txt', 'w')
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
