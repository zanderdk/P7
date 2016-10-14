# Compare Algorithms
import pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn import linear_model
from sklearn.model_selection import KFold, cross_val_score
from sklearn.linear_model import Ridge, LinearRegression
from sklearn import preprocessing 
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
import sys

filename = sys.argv[1]

# load dataset
dataframe = pandas.read_csv(filename, delim_whitespace=True, header=None)
array = dataframe.values

min_max_scaler = preprocessing.MinMaxScaler()
# normalize the page ratio to be within [0, 1] 
dataframe[4] = min_max_scaler.fit_transform(dataframe[4])

X = array[:,0:5]
Y = array[:,5]
# prepare configuration for cross validation test harness
num_folds = 10
seed = 7
# prepare models
models = []
models.append(('LR', LinearRegression()))
models.append(('Ridge', Ridge()))
#models.append(('ARDRegression', linear_model.ARDRegression()))
models.append(('Lasso', linear_model.Lasso()))
models.append(('LassoCV', linear_model.LassoCV()))
models.append(('LassoLars', linear_model.LassoLars()))

def keras_baseline_model():
	# create model
	model = Sequential()
	model.add(Dense(3, input_dim=5, init='normal', activation='sigmoid'))
	model.add(Dense(1, init='normal', activation="sigmoid"))
	# Compile model
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model
models.append(('Keras', KerasRegressor(build_fn=keras_baseline_model, nb_epoch=1, batch_size=5, verbose=0)))

# TODO ValueError: Unknown label type: (array([ 0.23]),) 
#models.append(('Perceptron', linear_model.Perceptron()))

# TODO TypeError: orthogonal_mp() missing 2 required positional arguments: 'X' and 'y'  
#models.append(('orthogonal_mp', linear_model.orthogonal_mp()))

# evaluate each model in turn
results = []
names = []
scoring = 'neg_mean_absolute_error'
for name, model in models:
	kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
	cv_results = cross_val_score(model, X, Y, cv=kfold, scoring=scoring)
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
