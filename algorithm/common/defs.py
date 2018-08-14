import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
par_dir = os.path.dirname(current_dir)

PARSED_DIR = par_dir + "/parsed/"
MODEL_DIR = par_dir + '/models/'
DATA_DIR = par_dir + "/data/"
LOG_PATH = par_dir + "/data/"

PORT_NAME = "COM4"

CLASS_NUM = 6
TEST_POINT_NUM = 14
SENSOR_NUM = 15
ADC_NUM = 6
ARDU_DELAY = 0.02
DELTA_STD = 1e-4

WINDOW_SIZE = 20