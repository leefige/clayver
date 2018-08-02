from sklearn.cluster import KMeans
import numpy as np

def getFeature(windows):
    for anaNo in range(6):
        print("anaNo = %d" % anaNo)
        _X = []
        for window in windows:
            feat = []
            feat.extend([window.getMax(anaNo), window.getMin(anaNo), window.getMean(anaNo)])
            _X.append(feat)
        # print(_X)
        X = np.array(_X)
        print(X.shape)
        clf = KMeans(n_clusters=2).fit(X)
        print(clf.cluster_centers_)

        labels = clf.labels_
        # print(labels)
        start = 0
        clusters = []
        total = len(labels)
        for i in range(1, total):
            if labels[i] != labels[start] or i == total - 1:
                clusters.append((start, i))
                start = i + 1
        for clus in clusters:
            print("(%d, %d): %d" % (clus[0], clus[1], clus[1] - clus[0] + 1))
        print()

    print("anaNo = 0~5")
    _X = []
    for window in windows:
        feat = []
        for i in range(0, 6):
            feat.extend([window.getMean(i)])
        _X.append(feat)
    # print(_X)
    X = np.array(_X)
    print(X.shape)
    clf = KMeans(n_clusters=2).fit(X)
    print(clf.cluster_centers_)

    labels = clf.labels_
    # print(labels)
    start = 0
    clusters = []
    total = len(labels)
    for i in range(1, total):
        if labels[i] != labels[start] or i == total - 1:
            clusters.append((start, i))
            start = i + 1
    for clus in clusters:
        print("(%d, %d): %d" % (clus[0], clus[1], clus[1] - clus[0] + 1))
    print()



def getFeature_bias(windows):
    for anaNo in range(6):
        print("anaNo = %d" % anaNo)
        _X = []
        for window in windows:
            feat = []
            feat.extend([window.getMax(anaNo), window.getMin(anaNo), window.getMean(anaNo)])
            _X.append(feat)
        # print(_X)
        X = np.array(_X)
        print(X.shape)
        clf = KMeans(n_clusters=2).fit(X)
        print(clf.cluster_centers_)

        labels = clf.labels_
        # print(labels)
        start = 0
        clusters = []
        total = len(labels)
        for i in range(1, total):
            if labels[i] != labels[start] or i == total - 1:
                clusters.append((start, i))
                start = i + 1
        for clus in clusters:
            print("(%d, %d): %d" % (clus[0], clus[1], clus[1] - clus[0] + 1))
        print()

    print("anaNo = 0~5")
    _X = []
    for window in windows:
        feat = []
        for i in range(0, 6):
            feat.extend([window.getMean(i)])
        _X.append(feat)
    # print(_X)
    X = np.array(_X)
    print(X.shape)
    clf = KMeans(n_clusters=2).fit(X)
    print(clf.cluster_centers_)

    labels = clf.labels_
    # print(labels)
    start = 0
    clusters = []
    total = len(labels)
    for i in range(1, total):
        if labels[i] != labels[start] or i == total - 1:
            clusters.append((start, i))
            start = i + 1
    for clus in clusters:
        print("(%d, %d): %d" % (clus[0], clus[1], clus[1] - clus[0] + 1))
    print()