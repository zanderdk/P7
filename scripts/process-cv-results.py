import pickle
import pprint

# Method must be available to unpickle KerasClassifier
def keras_baseline_model():
    pass

results = []
with open("cv_results.p", "rb") as results_file:
    results = pickle.load(results_file)

pp = pprint.PrettyPrinter()
print(len(results))
for res in results:
    pp.pprint(res)
