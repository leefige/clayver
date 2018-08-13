import os, sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from random import shuffle
from sys import argv

import numpy as np
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB as NB
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier as DT

from common.utility import *
from common.defs import *

def filter_local(data:list):
    sorted(data, key=lambda x : x['tp'])
    res = []
    for i in range(WINDOW_SIZE, len(data)):
        mean = []
        std = []
        curLi = data[i - WINDOW_SIZE:i]
        for j in range(ADC_NUM):
            mean.append(np.mean([sp['data'][j] for sp in curLi]))
            std.append(np.std([sp['data'][j] for sp in curLi]))
        point = {}
        point['label'] = data[i]['label']
        point['tp'] = data[i]['tp']
        point['raw'] = data[i]['data']
        point['data'] = []
        for j in range(ADC_NUM):
            dividor = std[j] if std[j] != 0 else DELTA_STD
            point['data'].append((data[i]['data'][j] - mean[j]) / dividor)
        for j in range(ADC_NUM, SENSOR_NUM):
            point['data'].append(data[i]['data'][j] - data[i - 1]['data'][j])
        res.append(point)
    return res

def genData():
    data = json_loadAll()

    classes = {}
    classes['idle'] = []
    classes['dynamic'] = []

    for sp in data:
        key = sp['label']
        if key == -1:
            classes['idle'].append(sp['data'])
        else:
            classes['dynamic'].append(sp['data'])
    
    lenMin = min(len(classes['idle']), len(classes['dynamic']))
    shuffle(classes[-1])
    data_0 = classes[-1][:avrLen]

    _X = []
    y = []
    if gen_idle:
        _X = [da[:SENSOR_NUM] for da in data_0]
        y = np.ones(len(data_0)) * -1
    for i in range(CLASS_NUM):
        _X.extend([da[:SENSOR_NUM] for da in classes[i]])
        y = np.append(y, np.ones(len(classes[i])) * i)
    
    X = np.array(_X)
    y = np.array(y)
    return X, y

def classify(X, y, clf):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    clf.fit(X_train, y_train)

    y_pre = clf.predict(X_test)
    cnt = 0
    for i in range(len(y_pre)):
        if y_test[i] == y_pre[i]:
            cnt += 1
    
    # print(y_test)
    # print(y_pre)
    # print("Precision: %f" % (cnt / len(y_test)))
    return cnt / len(y_test)

if __name__ == '__main__':
    X, y = genData()
    print("X.shape:", X.shape)
    print("y.shape:", y.shape)
    clas = []
    clas.append(["KNN", KNN(n_neighbors=6)])
    clas.append(["SVC", SVC()])
    clas.append(["DT", DT()])
    clas.append(["NB", NB()])
    # cla = KNN(n_neighbors=6)
    clfIdx = 0
    savedClfs = [None] * 4
    bestPre = [0] * 4
    for clf in clas:
        pres = []
        for i in range(2000):
            p = classify(X, y, clf[1])
            if p > bestPre[clfIdx]:
                bestPre[clfIdx] = p
                savedClfs[clfIdx] = clf[1]
            pres.append(p)
        print("%s precision: %f" % (clf[0], np.mean(pres)))
        joblib.dump(savedClfs[clfIdx], MODEL_DIR + clf[0] + '.pkl')
        clfIdx += 1

    # check if written
    print("Using saved models:")
    for clf in clas:
        clf[1] = joblib.load(MODEL_DIR + clf[0] + '.pkl')
        p = classify(X, y, clf[1])
        print("%s precision: %f" % (clf[0], p))
