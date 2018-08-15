import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from random import shuffle
from lstm import LSTM_model
from common.defs import *
from common.sample import *
from common.utility import *
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from keras.models import load_model

# FEAT_LEN = 10
FEED_LEN = 10

def getData(class_num=CLASS_NUM):
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

# data: non-idle list
def genFeature(data:list):
    assert len(data) == FEED_LEN + 1
    mean = []
    std = []
    rang = []
    for i in range(ADC_NUM):
        tmpLi = [da[i] for da in data]
        mean.append(np.mean(tmpLi))
        std.append(np.std(tmpLi))
        rang.append(max(tmpLi) - min(tmpLi))

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
    # if data[-1].label == -1:
    #     print(data[-1].label)
    label = data[-1].label if data[-1].label != -1 else CLASS_NUM
    return feed, label

def classify(X, y, class_num=CLASS_NUM, init_epo=None, epo=1000):
    if not init_epo:
        lstm = LSTM_model(class_num + 1, feed_length=FEED_LEN, feed_dim=ADC_NUM * 7)
        lstm.fit(X, y, batch_size=64, epochs=300, validation_split=0.2)
    else:
        lstm = load_model(MODEL_DIR + "lstm_%d.hdf5" % class_num)
        lstm.fit(X, y, batch_size=64, epochs=epo, validation_split=0.2, initial_epoch=init_epo)
    lstm.save(MODEL_DIR + "lstm_%d.hdf5" % class_num)

if __name__ == '__main__':
    # TODO: note: class num
    class_num = CLASS_NUM
    allData = getData(class_num)
    print("Preparing data...")
    Xy = []
    for i in range(FEED_LEN + 1, len(allData)):
        feed, label = genFeature(allData[i-(FEED_LEN + 1):i])
        Xy.append([feed, label])
    
    shuffle(Xy)
    X = [it[0] for it in Xy]
    y = [it[1] for it in Xy]

    X = np.array(X)
    y = np.array(y)
    y = to_categorical(y, class_num + 1)
    print(y.shape)

    print("Start to classify...")
    classify(X, y, class_num=class_num, init_epo=1000, epo=1300)
