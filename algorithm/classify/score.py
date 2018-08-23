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

FEED_LEN = 10

def getData(class_num):
    allData = json_loadAll(class_num)
    sorted(allData, key=lambda x : x.tp)

    # pick out idle
    idleLi = []
    nonIdleLi = []
    inIdle = False
    curIdle = []
    for i in range(len(allData)):
        da = allData[i]
        if not inIdle:
            if da.label == -1:
                inIdle = True
                curIdle.append(da)
                da.setRelated(curIdle)
            else:
                da.setRelated(idleLi[-1])
                nonIdleLi.append(da)
        else:
            if da.label == -1:
                curIdle.append(da)
                da.setRelated(curIdle)
            else:
                inIdle = False
                idleLi.append(curIdle)
                da.setRelated(idleLi[-1])
                nonIdleLi.append(da)
                curIdle = []
        # last one
        if i == len(allData) - 1:
            if da.label == -1:
                idleLi.append(curIdle)
            else:
                nonIdleLi.append(da)

    print("Related idle list added")
    for non in nonIdleLi:
        assert non.relatedIdle != None
    idleCnt = 0
    for idl in idleLi:
        idleCnt += len(idl)
        for idl_i in idl:
            assert idl_i.relatedIdle != None
        
    assert idleCnt + len(nonIdleLi) == len(allData)
    return allData

# feature based on idle data (bias from idle state)
def genFeature_idle(spl:Sample):
    # get idle data
    idleMean = []
    idleStd = []
    idleRange = []
    for i in range(ADC_NUM):
        tmpLi = [idl[i] for idl in spl.relatedIdle]
        idleMean.append(np.mean(tmpLi))
        idleStd.append(np.std(tmpLi))
        idleRange.append(max(tmpLi) - min(tmpLi))
    # generate feature
    res = []
    for i in range(ADC_NUM):
        res.append(idleStd[i])
        res.append(idleRange[i])
        res.append(spl[i] - idleMean[i])
    return res


# feature based on sliding window (bias within a local sliding window)
def genFeature(data:list, class_num:int):
    assert len(data) == FEED_LEN + 1
    mean = []
    std = []
    rang = []
    for i in range(ADC_NUM):
        tmpLi = [da[i] for da in data]
        mean.append(np.mean(tmpLi))
        std.append(np.std(tmpLi))
        rang.append(max(tmpLi) - min(tmpLi))
    # generate feature
    feed = []
    for i in range(1, len(data)):
        res = genFeature_idle(data[i])
        for j in range(ADC_NUM):
            res.append(std[j])
            res.append(rang[j])
            res.append(data[i][j] - data[i-1][j])
            res.append(data[i][j] - mean[j])
        assert len(res) == ADC_NUM * 7
        feed.append(res)
    assert len(feed) == FEED_LEN
    # annotation; if label is -1, replace it with class_num
    label = data[-1].label # if data[-1].label != -1 else class_num
    return feed, label

# config lstm
# if init_epo specified, will continue training the last model
def classify(X, y, target, init_epo=None, epo=1000):
    if not init_epo:
        lstm = LSTM_model(2, feed_length=FEED_LEN, feed_dim=ADC_NUM * 7)
        lstm.fit(X, y, batch_size=64, epochs=epo, validation_split=0.5)
    else:
        lstm = load_model(SCORE_MODEL_DIR + "score_%d.hdf5" % target)
        lstm.fit(X, y, batch_size=64, epochs=epo, validation_split=0.5, initial_epoch=init_epo)
    lstm.save(SCORE_MODEL_DIR + "score_%d.hdf5" % target)

# main
if __name__ == '__main__':
    usage = "Usage: python %s -c class [-r]\n\t-c: specify class\n\t-r: reload parsed data and save numpy array of feed in './feed/'"

    # TODO: note: change class num here!!!
    class_num = 2
    reloadData = False
    getClass = False
    target = -1

    opts, args = getopt.getopt(sys.argv[1:],"rhc:")
    for name, val in opts:
        if name == '-h':
            print(usage)
            exit(-1)
        elif name == '-r':
            reloadData = True
        elif name == '-c':
            getClass = True
            target = int(val)
        else:
            print("Warning: invalid opt: '%s'" % name)


    if not getClass:
        print("'-c class' required")
        exit(-2)

    if reloadData:
        print("Preparing data...")
        allData = getData(6)

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
        print("\nFinished!")
        saveFeature(Xy, FEED_DIR + 'Xy' + '.json')
    else:
        print("Loading data...")
        Xy = loadFeature(FEED_DIR + 'Xy' + '.json')

    print("Dividing data into classes...")
    thisClass = []
    notThisClass = []
    for pair in Xy:
        if pair[1] == target:
            thisClass.append(pair)
        else:
            notThisClass.append(pair)
    shuffle(notThisClass)
    notThisClass = notThisClass[:len(thisClass)]
    Xy = thisClass + notThisClass
    shuffle(Xy)

    X = [it[0] for it in Xy]
    y = [it[1] for it in Xy]
    positiveCnt = 0
    for i in range(len(y)):
        if y[i] == target:
            y[i] = 1
            positiveCnt += 1
        else:
            y[i] = 0

    X = np.array(X)
    y = np.array(y)
    # change to one-hot vector
    y = to_categorical(y, class_num)
    print("X.shape:", X.shape)
    print("y.shape:", y.shape)
    print("positiveCnt:", positiveCnt)
    print("y[:5]:", y[:5])
    print("Start to classify...")
    classify(X, y, target, epo=1700)
