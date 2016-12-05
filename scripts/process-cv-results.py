import pickle
import pprint

# Method must be available to unpickle KerasClassifier
def keras_baseline_model():
    pass

results = []
with open("cv_results_2_fold.p", "rb") as results_file:
    results = pickle.load(results_file)

pp = pprint.PrettyPrinter()
print(len(results))

names = list(map(lambda x: x["name"], results))

for res in results:
    pp.pprint(res)

print(names)