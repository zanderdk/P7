from multiprocessing import Process, Manager
import time
import pickle
import numpy as np
from sklearn.model_selection import KFold, cross_val_predict
from sklearn import metrics
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier, PassiveAggressiveClassifier, Perceptron
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from keras.wrappers.scikit_learn import KerasClassifier
from keras.models import Sequential
from keras.layers import Dense

Z = []
with open("training_vectors_stack.tsv", "rb") as fil:
    Z = pickle.load(fil)

X = np.array([x for x, y in Z])
Y = np.array([y for x, y in Z])

print("Positivies: " + str(len([x for x in Y if x == 1])))
print("Negatives: " + str(len([x for x in Y if x == 0])))

num_features = len(X[0])
num_folds = 2
seed = 7

# Prepare models
models = []

# Non-Ensemble classifiers to be included in classifer test with default params
# Some classifiers have non-default params to reduce training time significantly
models.append(('Dummy', DummyClassifier(strategy="uniform")))
models.append(('LogisticRegression', LogisticRegression(C=0.001)))
models.append(('Ridge', RidgeClassifier())) # Non-probabilistic
models.append(('Perceptron', Perceptron())) # Non-probabilistic
models.append(('PassiveAggressive', PassiveAggressiveClassifier(C=0.001))) # Non-probabilistic
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('QDA', QuadraticDiscriminantAnalysis()))
models.append(('Naive_Bayes_Gaussian', GaussianNB()))
models.append(('LinearSVC', LinearSVC(C=0.001))) # Non-probabilistic
models.append(('DecisionTree', DecisionTreeClassifier(max_depth=5)))
models.append(("NearestCentroid", NearestCentroid())) # Non-probabilistic
models.append(("KNN_5", KNeighborsClassifier(n_neighbors=5)))
models.append(('MultiLayerPerceptron', MLPClassifier()))

def keras_baseline_model():
    model = Sequential()
    model.add(Dense(64, input_dim=num_features, init='normal', activation="relu"))
    model.add(Dense(1, init='normal', activation="relu"))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer="adam")
    return model

models.append(('Keras', KerasClassifier(build_fn=keras_baseline_model, nb_epoch=5, batch_size=100, verbose=0)))

manager = Manager()
shared_results = manager.list()
def test_func(model, name, X, Y, seed, num_folds):
    print("Started " + name)
    kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
    start = time.time()
    predicted = cross_val_predict(model, X, y=Y, cv=kfold)
    end = time.time()
    duration = end - start
    # Get the different scores + confusion matrix
    confusion_matrix = metrics.confusion_matrix(Y, predicted)
    confusion_matrix_normalized = confusion_matrix.astype("float") / confusion_matrix.sum(axis=1),
    scores = {
        "confusion_matrix": confusion_matrix,
        "confusion_matrix_normalized": confusion_matrix_normalized,
        "accuracy": metrics.accuracy_score(Y, predicted),
        "precision": metrics.precision_score(Y, predicted),
        "recall": metrics.recall_score(Y, predicted),
        "f_score": metrics.f1_score(Y, predicted)
    }
    # Save the results
    res = {
        "name": name,
        "params": model.get_params(),
        "duration": duration,
        "scores": scores
    }
    shared_results.append(res)
    print("Done with %s in %f seconds" % (name, duration))

# Evaluate each model in turn
all_processes = [Process(target=test_func, args=(model, name, X, Y, seed, num_folds)) for name, model in models]
for process in all_processes:
    process.start()
for process in all_processes:
    process.join()

with open("cv_results.p", "wb") as results_file:
    results = list(shared_results)  # Back to regular list for easier unpickling
    pickle.dump(results, results_file)
