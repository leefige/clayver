import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)

from defs import *
import serial

TIME_OUT_SECOND = 1
BAUDRATE = 9600

def initSerial(port):
    try:
        ser = serial.Serial(port, baudrate=BAUDRATE, timeout=TIME_OUT_SECOND)
    except serial.SerialException: 
        print("Error: cannot open Serial '%s'!" % port)
        exit(-1)
    return ser

def readline(serial: serial.Serial):
    line = serial.readline()
    try:
        line = line.decode('utf-8')
    except UnicodeDecodeError:
        line = ""
    return line.strip()

def writeline(serial: serial.Serial, data):
    return serial.write(str(data) + '\n\r')
