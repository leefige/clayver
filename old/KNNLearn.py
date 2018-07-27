from __future__ import division
import numpy as np
from sklearn import neighbors
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier as DT

from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
import pdb

modelPath = './models/'

# feature1 = np.loadtxt('evaluate/90g_1.txt')
# feature1 = feature1[0:5,:]
# print(feature1.shape)
# feature2 = np.loadtxt('evaluate/90g_2.txt')
# feature2 = feature2[0:5,:]
# print(feature2.shape)
# feature3 = np.loadtxt('evaluate/90g_3.txt')
# feature3 = feature3[0:5,:]
# print(feature3.shape)
# feature4 = np.loadtxt('evaluate/90g_4.txt')
# feature4 = feature4[0:5,:]
# print(feature4.shape)
# feature5 = np.loadtxt('evaluate/90g_5.txt')
# feature5 = feature5[0:5,:]
# print(feature5.shape)
# feature6 = np.loadtxt('evaluate/90g_6.txt')
# feature6 = feature6[0:5,:]
# print(feature6.shape)
# feature7 = np.loadtxt('evaluate/90g_7.txt')
# feature7 = feature7[0:5,:]
# print(feature7.shape)
# feature8 = np.loadtxt('evaluate/90g_8.txt')
# feature8 = feature8[0:5,:]
# print(feature8.shape)
# X = np.concatenate((feature1,feature2,feature3,feature4,feature5,feature6,feature7,feature8),axis=0)


def classify(filename, each_len=10):
	# X = np.loadtxt('evaluate/40min.txt')
	X = np.loadtxt(filename)

	print(X.shape)
	# X = np.delete(X, [5,10,11,13,19,20,26,27,28,34,40,41,42,48,49,55], 0)
	# 
	# controller each 20 samples
	# w = np.loadtxt('train/eye.txt')
	# a = np.loadtxt('train/mouth.txt')
	# d = np.loadtxt('train/ear.txt')
	# m = np.loadtxt('train/wing.txt')
	# c = np.loadtxt('train/chest.txt')
	# b = np.loadtxt('train/back.txt')
	# X = np.concatenate((w,a,d,m,c),axis=0)

	# X = np.loadtxt('evaluate/15min.txt')
	# print("X.shape:")
	# print(X.shape)

	# 40min
	# y = np.ones(5)
	# for i in range(7):
	# 	y = np.append(y,np.ones(5)*(i+2))
	# print(y)

	y = np.ones(each_len)
	for i in range(7):
		y = np.append(y,np.ones(each_len)*(i+2))
	# print("y:")
	# print(y)

	# pdb.set_trace()
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

	# KNN
	clf = neighbors.KNeighborsClassifier(n_neighbors=3)
	clf.fit(X_train, y_train)
	joblib.dump(clf,modelPath+'owl.pkl')
	clf = joblib.load(modelPath+'owl.pkl')
	y_score = clf.predict(X_test)

	precise=np.sum(y_score == y_test)/len(y_test)
	# print("3-NN")
	# print(y_score)
	# print(y_test)
	print("3-NN:%.6f" % precise)

	# Linear SVC
	clf = LinearSVC()
	clf.fit(X_train, y_train)
	joblib.dump(clf,modelPath+'owl_svm.pkl')
	clf = joblib.load(modelPath+'owl_svm.pkl')
	y_score = clf.predict(X_test)

	precise=np.sum(y_score == y_test)/len(y_test)
	# print("SVC")
	# print(y_score)
	# print(y_test)
	print("SVC:%.6f" % precise)

	# Naive Bayes
	clf = GaussianNB()
	clf.fit(X_train, y_train)
	joblib.dump(clf,modelPath+'owl_gnb.pkl')
	clf = joblib.load(modelPath+'owl_gnb.pkl')
	y_score = clf.predict(X_test)

	precise=np.sum(y_score == y_test)/len(y_test)
	# print("Bayes")
	# print(y_score)
	# print(y_test)
	print("Bayes:%.6f" % precise)

	# DT
	clf = DT()
	clf.fit(X_train, y_train)
	joblib.dump(clf,modelPath+'owl_dt.pkl')
	clf = joblib.load(modelPath+'owl_dt.pkl')
	y_score = clf.predict(X_test)

	precise=np.sum(y_score == y_test)/len(y_test)
	# print("c")
	# print(y_score)
	# print(y_test)
	print("DT:%.6f" % precise)



	# precision = dict()
	# recall = dict()
	# average_precision = dict()
	# for i in range(n_classes):
	#     precision[i], recall[i], _ = precision_recall_curve(y_test[:, i],
	#     average_precision[i] = average_precision_score(y_test[:, i], y_score[:, i])
	# precision["micro"], recall["micro"], _ = precision_recall_curve(y_test.ravel(),
	#     y_score.ravel())
	# average_precision["micro"] = average_precision_score(y_test, y_score,
	#                                                      average="micro")
	# print('Average precision score, micro-averaged over all classes: {0:0.2f}'
	#       .format(average_precision["micro"]))

