import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
par_dir = os.path.dirname(current_dir)

PARSED_DIR = par_dir + "/parsed/"
MODEL_DIR = par_dir + '/models/'
SCORE_DIR = par_dir + '/score/'
SCORE_MODEL_DIR = SCORE_DIR + 'models/'
SCORE_FIG_DIR = SCORE_DIR + 'figs/'
SCORE_RAW_DIR = SCORE_DIR + 'raws/'
DATA_DIR = par_dir + "/data/"
LOG_PATH = par_dir + "/data/"
FEED_DIR = par_dir + "/feed/"

PORT_NAME = "COM4"

CLASS_NUM = 6
TEST_POINT_NUM = 6
SENSOR_NUM = 15
ADC_NUM = 6

# delay of arduino
ARDU_DELAY = 0.02

# used to avoid 'divided by zero' 
DELTA_STD = 1e-4

WINDOW_SIZE = 10
