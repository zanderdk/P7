import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pickle

results = []
names = []

for file in os.listdir("."):
    if file.endswith("cv_results") and os.stat(file).st_size != 0:
        with open(file, "rb") as file_open:
            time, name, cv_result = pickle.load(file_open)
            results.append(cv_result)
            names.append(name)

fig = plt.figure()
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(results)
ax.set_xticklabels(names)
fig.savefig("algorithm-comparison.png")
