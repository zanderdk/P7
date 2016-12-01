import pandas
import sys
from gensim.models import Word2Vec
import random
import gc
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.linear_model import SGDClassifier
from sklearn.dummy import DummyClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import KFold, cross_val_score
from sklearn import tree
from keras.wrappers.scikit_learn import KerasClassifier
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import itertools
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score
import pickle
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

from multiprocessing import Process, Manager
import multiprocessing

Z = []
with open("node2vec-parameter-optimization/training_vectors_stack.tsv", "rb") as fil:
    Z = pickle.load(fil)

X = np.array([x for x,y in Z])
Y = np.array([y for x,y in Z])

print("positivies:" + str(len([x for x in Y if x == 1])))
print("negatives:" + str(len([x for x in Y if x == 0])))

num_folds = 3
seed = 7

num_features = len(X[0])

# prepare models
models = []
# sanity check
models.append(('Dummy', DummyClassifier("uniform")))
models.append(('SGD', SGDClassifier(loss="hinge", penalty="l2")))
#models.append(('Nearest Neighbors', KNeighborsClassifier(3)))
#models.append(('Linear_SVM', SVC(kernel="linear", C=0.025)))
#models.append(('RBF_SVM', SVC(gamma=2, C=1)))
#models.append(('Gaussian_Process', GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True)))
models.append(('Decision_Tree1', DecisionTreeClassifier(max_depth=5)))
models.append(('Decision_Tree2', DecisionTreeClassifier(max_depth=5, criterion="entropy")))
models.append(('Decision_Tree3', DecisionTreeClassifier(max_depth=None)))
models.append(('Decision_Tree4', DecisionTreeClassifier(max_depth=None, max_features=100)))
#models.append(('Random_Forest', RandomForestClassifier(max_depth=None, n_estimators=10, max_features=None)))
#models.append(('AdaBoost', AdaBoostClassifier()))
#models.append(('Naive_Bayes', GaussianNB()))
#models.append(('QDA', QuadraticDiscriminantAnalysis()))

def keras_baseline_model(x = 32, act = "relu", act2 = "relu", opti = "adam"):
    # create model
    model = Sequential()
    model.add(Dense(x, input_dim=num_features, init='normal', activation=act))
    model.add(Dense(1, init='normal', activation=act2))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer=opti)
    return model

#models.append(('Keras', KerasClassifier(build_fn=lambda: keras_baseline_model(64, "relu", "relu", "adam"), nb_epoch=10, batch_size=100, verbose=1)))

#models.append(('Neural_Net', MLPClassifier(alpha=1)))

#models.append(('Gradient Boosting', GradientBoostingClassifier()))


# evaluate each model in turn
results = []
names = []


def test_func(model, name, X, Y, seed, num_folds):
    with open(name + "cv_results", "wb") as cv_results_file:
        scoring = 'f1'
        start = time.time()
        kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
        cv_results = cross_val_score(model, X, y=Y, cv=kfold, scoring=scoring)
        end = time.time()
        result = (end - start, name, cv_results)
        pickle.dump(result, cv_results_file)

all_processes = [Process(target=test_func, args=(model, name, X, Y, seed, num_folds)) for name, model in models]

for process in all_processes:
    process.start()

for process in all_processes:
    process.join()