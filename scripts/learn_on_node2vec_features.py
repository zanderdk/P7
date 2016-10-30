from gensim.models import Word2Vec
import sys
from sklearn.linear_model import SGDClassifier
from sklearn.dummy import DummyClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import KFold, cross_val_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn import tree
from keras.wrappers.scikit_learn import KerasClassifier
from keras.models import Sequential
from keras.layers import Dense
import numpy as np

# load the model containing features
model = Word2Vec.load_word2vec_format("modelUndirectedClickRate.bin" , binary=False)

X = []
Y = []

# load all training pairs
i = 0
for line in sys.stdin:
    source, target, label = tuple(line.split("\t"))
    
    if source in model and target in model:
        features_source = model[source]
        features_target = model[target]
        features = features_source * features_target
        Y.append(int(label))
        X.append(features)
    else:
        i += 1

print(len([x for x in Y if x == 0]))
print(len([x for x in Y if x == 1]))
print(i)
X = np.array(X)
Y = np.array(Y)

# prepare configuration for cross validation test harness
num_folds = 10
seed = 7
# prepare models
models = []
models.append(('SGD', SGDClassifier(loss="hinge", penalty="l2")))
#models.append(('Dec tree', tree.DecisionTreeClassifier()))

# sanity check
models.append(('Dummy', DummyClassifier("uniform")))

def keras_baseline_model():
    # create model
    model = Sequential()
    model.add(Dense(32, input_dim=64, init='normal', activation='relu'))
    model.add(Dense(1, init='normal', activation="relu"))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model
models.append(('Keras', KerasClassifier(build_fn=keras_baseline_model, nb_epoch=10, batch_size=128, verbose=0)))

# evaluate each model in turn
results = []
names = []
scoring = 'f1'
for name, model in models:
    kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
    cv_results = cross_val_score(model, X, y=Y, cv=kfold, scoring=scoring)
    results.append(cv_results)
    names.append(name)
    msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
    print(msg)
# boxplot algorithm comparison
fig = plt.figure()
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(results)
ax.set_xticklabels(names)
fig.savefig("algorithm-comparison.png")