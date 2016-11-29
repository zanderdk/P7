import pandas
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
import theano
theano.config.openmp = True

Z = []
with open("node2vec-parameter-optimization/training_vectors.tsv", "rb") as fil:
    Z = pickle.load(fil)

X = np.array([x for x,y in Z])
Y = np.array([y for x,y in Z])

num_folds = 3
seed = 7

num_features = len(X[0])

# prepare models
models = []
models.append(('SGD', SGDClassifier(loss="hinge", penalty="l2")))
# sanity check
models.append(('Dummy', DummyClassifier("uniform")))
def keras_baseline_model():
    # create model
    model = Sequential()
    model.add(Dense(32, input_dim=num_features, init='normal', activation='relu'))
    model.add(Dense(1, init='normal', activation="relu"))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model
models.append(('Keras', KerasClassifier(build_fn=keras_baseline_model, nb_epoch=10, batch_size=100, verbose=1)))

#models.append(('Gradient Boosting', GradientBoostingClassifier()))


# evaluate each model in turn
results = []
names = []
scoring = 'f1'
for name, model in models:
    print("-------------------------" + name + "-----------------------------------")
    kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
    cv_results = cross_val_score(model, X, y=Y, cv=kfold, scoring=scoring)
    results.append(cv_results)
    names.append(name)
    msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
    print(msg)
