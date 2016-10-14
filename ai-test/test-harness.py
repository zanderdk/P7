# Compare Algorithms
import pandas
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.model_selection import KFold, cross_val_score
from sklearn.linear_model import Ridge, LinearRegression
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor

# load dataset
dataframe = pandas.read_csv("wiki-train-example.csv", delim_whitespace=True, header=None)
array = dataframe.values
X = array[:,0:4]
Y = array[:,4]
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
	model.add(Dense(4, input_dim=4, init='normal', activation='relu'))
	model.add(Dense(1, init='normal'))
	# Compile model
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model
models.append(('Keras', KerasRegressor(build_fn=keras_baseline_model, nb_epoch=100, batch_size=5, verbose=0)))

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
plt.show()
