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

SENSOR_NUM = 6

def genData(name:str, gen_idle=True):
    data = json_load(name)

    classes = {}
    for i in range(-1, CLASS_NUM):
        classes[i] = []
    for sp in data:
        key = sp['label']
        classes[key].append(sp['data'])
    
    lens = []
    for i in range(CLASS_NUM):
        lens.append(len(classes[i]))
    avrLen = int(np.mean(lens))

    shuffle(classes[-1])
    data_0 = classes[-1][:avrLen]

    _X = []
    y = []
    if gen_idle:
        _X = data_0
        y = np.ones(len(data_0)) * -1
    for i in range(CLASS_NUM):
        _X.extend(classes[i])
        y = np.append(y, np.ones(len(classes[i])) * i)
    
    X = np.array(_X)
    return X, y

def classify(X, y, clf):
    # print(X.shape)
    # print(len(y))
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
    X, y = genData(argv[1], False)
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
