import sys
import pickle
import pprint
import csv

# Method must be available to unpickle KerasClassifier
def keras_baseline_model():
    pass

names = [
    'Baseline',
    'Logistic Regression',
    'Ridge Regression',
    'Perceptron',
    'Passive Aggressive',
    'Linear Discriminant Analysis',
    'Quadratic Discriminant Analysis',
    'Gaussian Naive Bayes',
    'Linear Support Vector Machine',
    'Decision Tree',
    'Nearest Centroid',
    'Multi Layer Perceptron',
    'Neural Network (Keras)'
]

results = []
with open("10f_results.p", "rb") as results_file:
    results = pickle.load(results_file)

results = [(name, res["scores"]["precision"], res["scores"]["recall"]) for name, res in zip(names, results)]
results.sort(key=lambda x: x[1], reverse=True)
header = ("name", "precision", "recall")

if len(sys.argv) > 1:
    with open(sys.argv[1], "w+", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        for res in results:
            writer.writerow(res)
    print(results)

else:
    print("Specify output file")
