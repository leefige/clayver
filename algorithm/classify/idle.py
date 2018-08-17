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
import matplotlib.pyplot as plt

from common.utility import *
from common.defs import *
from common.sample import *

def genWindows():
    allData = json_loadAll()
    sorted(allData, key=lambda x : x.tp)

    for i in range(ADC_NUM):
        tp = [da[i] for da in allData]
        plt.plot(tp)
    plt.show()
    
    wins = []
    for i in range(0, len(allData) - WINDOW_SIZE, 5):
        spl = allData[i:i + WINDOW_SIZE]
        wins.append(Window(spl))

    # generate pos & event
    for win in wins:
        win.decide()
    return wins

def genFeature(win:Window):
    res = []
    for i in range(ADC_NUM):
        res.append(win.range(i))
        res.append(win.std(i))
    return res

def genFeed():
    wins = genWindows()
    idleWin = []
    nonIdleWin = []

    for win in wins:
        if win.event == Window.eventType['idle']:
            idleWin.append(win)
        else:
            nonIdleWin.append(win)
    
    cnt = min(len(idleWin), len(nonIdleWin))

    shuffle(idleWin)
    shuffle(nonIdleWin)
    idleWin = idleWin[:cnt]
    nonIdleWin = nonIdleWin[:cnt]

    X = []
    y = []

    wins = idleWin + nonIdleWin
    shuffle(wins)

    for win in wins:
        X.append(genFeature(win))
        if win.event == Window.eventType['idle']:
            y.append(0)
        else:
            y.append(1)
    X = np.array(X)
    y = np.array(y)
    print("idle cnt: %d, non idle cnt: %d" % (len(idleWin), len(nonIdleWin)))
    print("X.shape:", X.shape)
    print("y.shape:", y.shape)
    return X, y


def classify(X, y, clf):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    clf.fit(X_train, y_train)

    y_pre = clf.predict(X_test)
    cnt = 0
    for i in range(len(y_pre)):
        if y_test[i] == y_pre[i]:
            cnt += 1
    
    return cnt / len(y_test)
    
if __name__ == '__main__':
    X, y = genFeed()
    clas = []
    clas.append(["KNN", KNN(n_neighbors=3)])
    # clas.append(["SVC", SVC()])
    clas.append(["DT", DT(max_depth=20)])
    clas.append(["NB", NB()])
    # cla = KNN(n_neighbors=6)
    clfIdx = 0
    savedClfs = [None] * 4
    bestPre = [0] * 4
    for clf in clas:
        pres = []
        for i in range(100):
            p = classify(X, y, clf[1])
            if p > bestPre[clfIdx]:
                bestPre[clfIdx] = p
                savedClfs[clfIdx] = clf[1]
            pres.append(p)
        print("%s precision: %f" % (clf[0], np.mean(pres)))
        joblib.dump(savedClfs[clfIdx], MODEL_DIR + "idle" + clf[0] + '.pkl')
        clfIdx += 1

    # check if written
    print("Using saved models:")
    for clf in clas:
        clf[1] = joblib.load(MODEL_DIR + "idle" + clf[0] + '.pkl')
        p = classify(X, y, clf[1])
        print("%s precision: %f" % (clf[0], p))
