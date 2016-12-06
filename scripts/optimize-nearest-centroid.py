import numpy as np
import pickle
from sklearn.neighbors import NearestCentroid
import pprint
from sklearn import metrics, preprocessing
from sklearn.model_selection import GridSearchCV

num_features = None
def load_data(limit=None, normalize=False):
    global num_features
    Z = []
    with open("training_vectors_stack.tsv", "rb") as f:
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

X, Y = load_data()
model = NearestCentroid()
parameters = {'metric':['cityblock', 'euclidean', 'l1', 'l2', 'manhattan', 'canberra'], 'shrink_threshold':np.arange(0,0.6,0.1)}
clf = GridSearchCV(model, parameters, scoring="precision", verbose=3, n_jobs=2)
clf.fit(X, Y)

pp = pprint.PrettyPrinter()
pp.pprint(clf.cv_results_)
pp.pprint(clf.best_params_)