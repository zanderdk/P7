import pickle
import argparse
import numpy as np
from sklearn.neighbors import NearestCentroid
from sklearn import preprocessing, metrics


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
    print("Positivies: " + str(len([x for x in Y if x == 1])))
    print("Negatives: " + str(len([x for x in Y if x == 0])))
    print("Average value: " + str(np.average(X)))
    print("Max value: " + str(np.amax(X)))
    print("Min value: " + str(np.amin(X)))
    num_features = len(X[0])
    return X, Y


print("Loading training data")
X, y = load_data("training_vectors_stack.tsv", None, True)

print("\nLoading test data")
X_test, y_test = load_data("test_data_vectors.tsv", None, True)

clf = NearestCentroid()

print("\nTraining model")
clf.fit(X, y)

predicted = clf.predict(X_test)

confusion_matrix = metrics.confusion_matrix(y_test, predicted)
confusion_matrix_normalized = confusion_matrix.astype('float') / confusion_matrix.sum(axis=0)
scores = {
    "confusion_matrix": confusion_matrix,
    "confusion_matrix_normalized": confusion_matrix_normalized,
    "accuracy": metrics.accuracy_score(y_test, predicted),
    "precision": metrics.precision_score(y_test, predicted),
    "recall": metrics.recall_score(y_test, predicted),
    "f1_score": metrics.f1_score(y_test, predicted),
    "f0.5_score": metrics.fbeta_score(y_test, predicted, beta=0.5),
    "f0.25_score": metrics.fbeta_score(y_test, predicted, beta=0.25),
    "f0.1_score": metrics.fbeta_score(y_test, predicted, beta=0.1)
}


print(scores)
