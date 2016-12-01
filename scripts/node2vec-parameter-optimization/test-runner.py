from node2vec import makeNodeModel, getAllNodes
import multiprocessing
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import KFold, cross_val_score
import numpy as np
import os
import pickle
import time
import sys

import sklearn.metrics.fbeta_score
import sklearn.metrics.make_scorer



# Write a function like this called 'main'
def main(job_id, params):
  with open("file_" + str(job_id), "w") as log_file:
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
    function = params["function"][0]
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
    log_file.write("Making model...\n")
    log_file.flush()
    start = time.time()
    model = makeNodeModel(p, q, l, r, d, k, directed, workers, nodes, log_file, save=False)
    end = time.time()
    print("Making model took: " + str(end - start) + " seconds")
    log_file.write("Making model took: " + str(end - start) + " seconds\n")
    log_file.flush()

    # save model using a file name that identifies the settings
    model_name = "node2vec-model-"
    model_name += "p=" + str(p) + "-"
    model_name += "q=" + str(q) + "-"
    model_name += "l=" + str(l) + "-"
    model_name += "r=" + str(r) + "-"
    model_name += "d=" + str(d) + "-"
    model_name += "k=" + str(k) + "-"
    model_name += "directed=" + str(directed)
    model_name += "function=" + str(function)

    # save the model for later use
    #start = time.time()
    #model.save_word2vec_format(model_name)
    
    #end = time.time()
    #print("Save model took: " + str(end - start) + " seconds")
    #log_file.write("Save model took: " + str(end - start) + " seconds\n")
    #log_file.flush()
    #print("Model generated and saved as file. I will now evaluate the model.")

    X_pos = []
    X_neg = []
    Y_pos = []
    Y_neg = []

    # load all training pairs
    i = 0
    with open('paropt_training_data.csv', 'r') as f:
      for line in f:
          source, target, label = tuple(line.split())

          if source in model and target in model:
              features_source = model[source]
              features_target = model[target]
              if(function == "hadamard"):
                features = features_source * features_target
              elif function == "divide":
                features = features_source / features_target
              elif function == "stack":
                features = np.concatenate((features_source, features_target), axis=0)
              else:
                sys.exit("fata error in function selection")
              if label == "0":
                Y_neg.append(int(label))
                X_neg.append(features)
              else:
                Y_pos.append(int(label))
                X_pos.append(features)
          else:
            i += 1

      len_pos = len(X_pos)
      len_neg = len(X_neg)
      print("before 50:50: neg len: " + str(len_neg))
      print("before 50:50: pos len: " + str(len_pos))
      print(i)
      # make sure that there is a 50:50 positive:negative ratio

      if len_pos > len_neg:
          # too many in positives
          X_pos = X_pos[:len_neg]
          Y_pos = Y_pos[:len_neg]
      else:
          # too many negatives
          X_neg = X_neg[:len_pos]
          Y_neg = Y_neg[:len_pos]


      X = X_neg + X_pos
      Y = Y_neg + Y_pos
      X = np.array(X)
      Y = np.array(Y)

    # prepare configuration for cross validation test harness
    num_folds = 10
    seed = 7
    # prepare models
    classifier = SGDClassifier(loss="hinge", penalty="l2")
    name = "SGD"

    # evaluate each model in turn
    scoring = make_scorer(fbeta_score, beta=0.5)
    kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
    cv_results = cross_val_score(classifier, X, y=Y, cv=kfold, scoring=scoring)
    msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
    print(msg)

    # we want to maximize the mean cross validation score, which means we want to minimize 1 - score
    return 1.0 - cv_results.mean()
