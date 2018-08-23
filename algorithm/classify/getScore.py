import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

import getopt
import json
from random import shuffle
from lstm import LSTM_model
from common.defs import *
from common.sample import *
from common.utility import *
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from keras.models import load_model, Model

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
Xy_bac = Xy
print("len(Xy)=", len(Xy))

print("Target: %d" % target)
thisClass = []
notThisClass = []
for pair in Xy:
    if pair[1] == target:
        thisClass.append(pair)
    else:
        notThisClass.append(pair)
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
TP = corCnt / len(X)
print("Pos accuracy: %.6f" % TP)

print("Getting output of softmax layer...")
dense_layer_model = Model(inputs=clf.input, outputs=clf.get_layer(name='softmax').output)
dense_output = dense_layer_model.predict(X)
scores = [it[1] for it in dense_output]
scores.sort()
plt.plot(scores)
plt.savefig(SCORE_FIG_DIR + 'fig_pos_%d.png' % target)

with open(SCORE_DIR + 'distribution_%d.txt' % target, 'w', encoding='utf8') as fout:
    mean = np.mean(scores)
    std = np.std(scores)
    maxS = max(scores)
    minS = min(scores)
    rangeS = maxS - minS

    fout.write("mean: %f\n" % mean)
    fout.write("std: %f\n" % std)
    fout.write("max: %f\n" % maxS)
    fout.write("min: %f\n" % minS)
    fout.write("range: %f\n" % rangeS)

with open(SCORE_RAW_DIR + 'scores_pos_%d.txt' % target, 'w', encoding='utf8') as fout:
    scores = [float(s) for s in scores]
    json.dump(scores, fout, ensure_ascii=False)



# do same thing for negative samples

Xy = notThisClass
shuffle(Xy)
X = [it[0] for it in Xy]
y = np.ones(len(X)) * 0

X = np.array(X)
y = np.array(y)
print("X.shape:", X.shape)
print("y.shape:", y.shape)

y_pre = clf.predict(X)
y_pre = [np.argmax(it) for it in y_pre]
print(y_pre[:20])

corCnt = 0
for i in range(len(X)):
    if y_pre[i] == y[i]:
        corCnt += 1
TN = corCnt / len(X)
print("Neg accuracy: %.6f" % TN)

dense_layer_model = Model(inputs=clf.input, outputs=clf.get_layer(name='softmax').output)
dense_output = dense_layer_model.predict(X)
scores = [it[1] for it in dense_output]
scores.sort()
plt.cla()
plt.plot(scores)
plt.savefig(SCORE_FIG_DIR + 'fig_neg_%d.png' % target)

with open(SCORE_DIR + 'distribution_%d.txt' % target, 'a', encoding='utf8') as fout:
    fout.write("\nneg:\n")
    mean = np.mean(scores)
    std = np.std(scores)
    maxS = max(scores)
    minS = min(scores)
    rangeS = maxS - minS

    fout.write("mean: %f\n" % mean)
    fout.write("std: %f\n" % std)
    fout.write("max: %f\n" % maxS)
    fout.write("min: %f\n" % minS)
    fout.write("range: %f\n\n" % rangeS)
    fout.write("TP: %f\n" % TP)
    fout.write("TN: %f\n" % TN)

with open(SCORE_RAW_DIR + 'scores_neg_%d.txt' % target, 'w', encoding='utf8') as fout:
    scores = [float(s) for s in scores]
    json.dump(scores, fout, ensure_ascii=False)
