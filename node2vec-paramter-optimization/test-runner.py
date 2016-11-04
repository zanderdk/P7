from node2vec import makeNodeModel, getAllNodes
import multiprocessing
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import KFold, cross_val_score
import numpy as np
import os
import pickle


# Write a function like this called 'main'
def main(job_id, params):
  print 'Anything printed here will end up in the output directory for job #:', str(job_id)
  print params

  # generate model with params
  p = float(params["p"][0])
  q = float(params["q"][0])
  
  l = int(params["l"][0])
  r = int(params["r"][0])
  d = int(params["d"][0])
  k = int(params["k"][0])
  directed = params["directed"][0] == "True"
  weighted = params["weighted"][0] == "True"
  workers = multiprocessing.cpu_count() # get the number of cores
  print("using %d workers" % workers)

  # check if the list of all nodes has already been loaded. If yes, just use that one
  if os.path.isfile("all_nodes.pickle"):
    print("Found all_nodes.pickle file, so loading that...")
    with open('all_nodes.pickle', 'r') as f:
      nodes = pickle.load(f)
  else:
    print("Could not find all_nodes.pickle file, so loading from the database...")
    nodes = getAllNodes()
    # write it to the pickle file
    with open('all_nodes.pickle', 'w') as f:
      pickle.dump(nodes, f)

  print("Making model...")
  model = makeNodeModel(p, q, l, r, d, k, directed, weighted, workers, nodes)

  # save model using a file name that identifies the settings
  model_name = "node2vec-model-"
  model_name += "p=" + str(p) + "-"
  model_name += "q=" + str(q) + "-"
  model_name += "l=" + str(l) + "-"
  model_name += "r=" + str(r) + "-"
  model_name += "d=" + str(d) + "-"
  model_name += "k=" + str(k) + "-"
  model_name += "weighted=" + str(weighted) + "-"
  model_name += "directed=" + str(directed)

  # save the model for later use
  model.save_word2vec_format(model_name)

  print("Model generated and saved as file. I will now evaluate the model.")

  X = []
  Y = []

  # load all training pairs
  i = 0
  with open('../scripts/trainingPairs.txt', 'r') as f:
    for line in f:
        source, target, label = tuple(line.split("\t"))

        if source in model and target in model:
            features_source = model[source]
            features_target = model[target]
            features = features_source * features_target
            Y.append(int(label))
            X.append(features)

    print(len([x for x in Y if x == 0]))
    print(len([x for x in Y if x == 1]))
    print(i)
    X = np.array(X)
    Y = np.array(Y)

  # prepare configuration for cross validation test harness
  num_folds = 3
  seed = 7
  # prepare models
  classifier = SGDClassifier(loss="hinge", penalty="l2")
  name = "SGD"

  # evaluate each model in turn
  scoring = 'precision'
  kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
  cv_results = cross_val_score(classifier, X, y=Y, cv=kfold, scoring=scoring)
  msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
  print(msg)

  # we want to maximize the mean cross validation score, which means we want to minimize 1 - score
  return 1.0 - cv_results.mean()