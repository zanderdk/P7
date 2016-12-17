import time
import pickle
import argparse
import numpy as np
from sklearn.model_selection import KFold, cross_val_predict
from sklearn import metrics, preprocessing
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier, PassiveAggressiveClassifier, Perceptron
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import NearestCentroid
from keras.wrappers.scikit_learn import KerasClassifier
from keras.models import Sequential
from keras.layers import Dense

# Load pickled training vectors
num_features = None
def load_data(input_file, limit=None, normalize=False):
    global num_features
    print("Loading training data from: " + input_file)
    Z = []
    with open(input_file, "rb") as f:
        Z = pickle.load(f)
    if limit is not None:
        Z = Z[:limit]
    X = np.array([x for x, y in Z])
    Y = np.array([y for x, y in Z])
    if normalize:
        scaler = preprocessing.MinMaxScaler()
        X = scaler.fit_transform(X)
    print("Total examples: " + str(len(Z)))
    print("Positivies: " + str(len([x for x in Y if x == 1])))
    print("Negatives: " + str(len([x for x in Y if x == 0])))
    print("Average value: " + str(np.average(X)))
    print("Max value: " + str(np.amax(X)))
    print("Min value: " + str(np.amin(X)))
    num_features = len(X[0])
    print("Number of features: " + str(num_features))
    return X, Y

# Neural network defined using Keras
def keras_baseline_model():
    model = Sequential()
    model.add(Dense(64, input_dim=num_features, init='normal', activation="relu"))
    model.add(Dense(1, init='normal', activation="relu"))
    # Compile model
    model.compile(loss='mse', optimizer="adam")
    return model

# Prepare the different models that should be tested
def prepare_models():
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
    models.append(('NearestCentroid', NearestCentroid())) # Non-probabilistic
    models.append(('MultiLayerPerceptron', MLPClassifier()))
    models.append(('Keras', KerasClassifier(build_fn=keras_baseline_model, nb_epoch=5, batch_size=100, verbose=0)))
    return models

# Cross validate a single classifier, and return the results
def test_classifier(model, name, X, Y, seed, num_folds):
    print("\nStarted " + name)
    kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
    start = time.time()
    predicted = cross_val_predict(model, X, y=Y, cv=kfold)
    end = time.time()
    duration = end - start
    # Get the different scores + confusion matrix
    confusion_matrix = metrics.confusion_matrix(Y, predicted)
    confusion_matrix_normalized = confusion_matrix.astype('float') / confusion_matrix.sum(axis=0)
    scores = {
        "confusion_matrix": confusion_matrix,
        "confusion_matrix_normalized": confusion_matrix_normalized,
        "accuracy": metrics.accuracy_score(Y, predicted),
        "precision": metrics.precision_score(Y, predicted),
        "recall": metrics.recall_score(Y, predicted),
        "f1_score": metrics.f1_score(Y, predicted),
        "f0.5_score": metrics.fbeta_score(Y, predicted, beta=0.5),
        "f0.25_score": metrics.fbeta_score(Y, predicted, beta=0.25),
        "f0.1_score": metrics.fbeta_score(Y, predicted, beta=0.1)
    }
    # Return the result
    result = {
        "name": name,
        "params": model.get_params(),
        "duration": duration,
        "scores": scores
    }
    print("Done with %s in %.2f seconds" % (name, duration))
    return result

# Evaluate the different classifiers
# Seed defined for reproducibility
def evaluate_classifiers(input_file, num_folds=10, limit=None, normalize=False, seed=7):
    results = []
    X, Y = load_data(input_file, limit, normalize)
    models = prepare_models()
    print("\nRunning %d-fold cross validation on %d classifiers" % (num_folds, len(models)))
    for name, model in models:
        results.append(test_classifier(model, name, X, Y, seed, num_folds))
    return results

# Save the pickled results
def store_results(results, out_file):
    with open(out_file, "wb") as results_file:
        pickle.dump(results, results_file)

# Main method that parses parameters and runs the test
def main():
    parser = argparse.ArgumentParser(description="Evaluates different classifiers")
    parser.add_argument("output_file", help="Name of output file")
    parser.add_argument("training_data", nargs="?", default="training_vectors_stack.tsv",
                        help="File containing training data")
    parser.add_argument("-n", "--normalize", action="store_true",
                        help="Normalize the training data")
    parser.add_argument("-l", "--limit", type=int, default=None,
                        help="Limit number of training examples used")
    parser.add_argument("-f", "--folds", type=int, default=10,
                        help="Specify number of folds to use. Default is 10")

    args = parser.parse_args()
    results = evaluate_classifiers(args.training_data, args.folds, args.limit, args.normalize)
    store_results(results, args.output_file)
    print("\nDone! Results saved as: " + args.output_file)

# Run main methdo when running the script
if __name__ == "__main__":
    main()
