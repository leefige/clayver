from utility import *
from sys import argv
import numpy as np
from random import shuffle
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.tree import DecisionTreeClassifier as DT
from sklearn.naive_bayes import BernoulliNB as NB
from sklearn.model_selection import train_test_split


def genData(name:str, gen_idle=True):
    data = json_load(name)
    lens = [len(data[str(i)]) for i in range(FEAT_SIZE)]
    
    avgLen = np.mean(lens)
    data_0 = data['-1']
    shuffle(data_0)
    data_0 = data_0[:int(avgLen)]

    _X = []
    y = []
    if gen_idle:
        _X = [di['data'] for di in data_0]
        y = np.ones(len(data_0)) * -1
    for i in range(FEAT_SIZE):
        _X.extend([di['data'] for di in data[str(i)]])
        y = np.append(y, np.ones(len(data[str(i)])) * i)
    
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
    for clf in clas:
        pres = []
        for i in range(5000):
            pres.append(classify(X, y, clf[1]))
        print("%s precision: %f" % (clf[0], np.mean(pres)))