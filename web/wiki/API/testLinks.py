import pandas
import matplotlib
import matplotlib.pyplot as plt
import sys
from gensim.models import Word2Vec
import random
import gc
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
import argparse
from sklearn.neighbors import NearestCentroid
from sklearn import preprocessing, metrics
from keras.wrappers.scikit_learn import KerasClassifier
from keras.models import Sequential
from keras.layers import Dense
from keras.layers.noise import GaussianNoise
from keras.layers.noise import GaussianDropout
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import PassiveAggressiveClassifier

dataframe = pandas.read_csv("training_labels2.tsv", delim_whitespace=True)

Word2VecModel = Word2Vec.load_word2vec_format('training_model.bin', binary=True)

def load_data(filename, limit=None, normalize=False):
    global num_features
    Z = []
    with open(filename, "rb") as f:
        Z = pickle.load(f)
    if limit is not None:
        Z = Z[:limit]
    X = np.array([x for x, y in Z])
    Y = np.array([y for x, y in Z])
    if normalize:
        scaler = preprocessing.MinMaxScaler()
        X = scaler.fit_transform(X)
    num_features = len(X[0])
    return X, Y

X, y = load_data("training.pickle", None, False)

def keras_baseline_model():
    model = Sequential()
    model.add(Dense(32, input_dim=64, init='normal', activation="relu"))
    model.add(Dense(1, init='normal', activation="sigmoid"))
    # Compile model
    model.compile(loss='mse', optimizer="adam")
    return model
model = KerasClassifier(build_fn=keras_baseline_model, nb_epoch=5, batch_size=100, verbose=0)
model.fit(X,y)

def test(title1, title2):
    vec1 = Word2VecModel[title1]
    vec2 = Word2VecModel[title2]
    concatVec = np.concatenate((vec1, vec2), axis=0).reshape(1,64)
    #print(concatVec.shape)
    return model.predict(concatVec)[0]

def testLinks(title, lst):
	arr = []
	for x in lst:
		if (test(title, x) == 1):
			arr.append(x)
	return arr