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

from position import *

testArr = ['8-29_0', '8-29_1']
# testArr = ['8-13_0', '8-13_1', '8-13_2', 'wcy', 'zjl']


if __name__ == '__main__':
    usage = "Usage: python %s [-r]\n\t-r: reload parsed data and save numpy array of feed in './feed/'"

    # TODO: note: change class num here!!!
    class_num = CLASS_NUM
    reloadData = False

    opts, args = getopt.getopt(sys.argv[1:],"rh")
    for name, val in opts:
        if name == '-h':
            print(usage)
            exit(-1)
        elif name == '-r':
            reloadData = True
        else:
            print("Warning: invalid opt: '%s'" % name)

    if reloadData:
        print("Preparing data...")
        allData = getData(class_num, file_names=testArr)

        # get pairs of (X, y), and shuffle
        print("Generating features...")
        Xy = []
        for i in range(FEED_LEN + 1, len(allData)):
            if i % 1000 == 0:
                print(str(i) + ' / ' + str(len(allData) - (FEED_LEN)), end='\r')
            feed, label = genFeature(allData[i-(FEED_LEN + 1):i], class_num)
            if label < 0:
                continue
            Xy.append([feed, label])
        print("\nFinished! Feed num: %d" % len(Xy))
        shuffle(Xy)
        X = [it[0] for it in Xy]
        y = [it[1] for it in Xy]
        saveFeature(X, FEED_DIR + 'test_X_%d' % class_num + '.json')
        saveFeature(y, FEED_DIR + 'test_y_%d' % class_num + '.json')
    else:
        print("Loading data...")
        X = loadFeature(FEED_DIR + 'test_X_%d' % class_num + '.json')
        y = loadFeature(FEED_DIR + 'test_y_%d' % class_num + '.json')

    y_true = y
    X = np.array(X)
    y = np.array(y)
    # change to one-hot vector
    y = to_categorical(y, class_num)
    print("X.shape:", X.shape)
    print("y.shape:", y.shape)
    print("Start to test...")
    
    clf = load_model(MODEL_DIR + "lstm_%d.hdf5" % class_num)
    y_pre = clf.predict(X)
    y_pre = [np.argmax(it) for it in y_pre]
    print(y_pre[:20])
    print(y_true[:20])

    corCnt = 0
    for i in range(len(X)):
        if y_pre[i] == y_true[i]:
            corCnt += 1
    TP = corCnt / len(X)
    print("Accuracy: %.6f" % TP)
