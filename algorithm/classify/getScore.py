import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

import getopt
from random import shuffle
from lstm import LSTM_model
from common.defs import *
from common.sample import *
from common.utility import *
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from keras.models import load_model

usage = "Usage: python %s -c class [-r]\n\t-c: specify class"

getClass = False
target = -1

opts, args = getopt.getopt(sys.argv[1:],"hc:")
for name, val in opts:
    if name == '-h':
        print(usage)
        exit(-1)
    elif name == '-c':
        getClass = True
        target = int(val)
    else:
        print("Warning: invalid opt: '%s'" % name)

if not getClass:
    print("'-c class' required")
    exit(-2)

print("Loading data...")
Xy = loadFeature(FEED_DIR + 'Xy' + '.json')
print("len(Xy)=", len(Xy))

print("Target: %d" % target)
thisClass = []
for pair in Xy:
    if pair[1] == target:
        thisClass.append(pair)
Xy = thisClass
shuffle(Xy)
X = [it[0] for it in Xy]
y = np.ones(len(X))

X = np.array(X)
y = np.array(y)
print("X.shape:", X.shape)
print("y.shape:", y.shape)

clf = load_model(SCORE_MODEL_DIR + "score_%d.hdf5" % target)
y_pre = clf.predict(X)
y_pre = [np.argmax(it) for it in y_pre]
print(y_pre[:20])

corCnt = 0
for i in range(len(X)):
    if y_pre[i] == y[i]:
        corCnt += 1
print("Accuracy: %.6f" % (corCnt / len(X)))


