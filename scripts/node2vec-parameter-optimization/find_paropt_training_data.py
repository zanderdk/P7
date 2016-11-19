# This file generates training data, making sure that the training samples do not include test data
import random
import sys

# this is the file we want to write to
with open("paropt_training_data.csv", "w") as training_data_file:
    negatives = []
    positives = []
    # load negatives from n grams method
    # the articles must be from featured -> featured/good
    with open("featured->featured_good_only_negatives.csv") as f:
        for line in f:
            source, target = tuple(line.split())
            negatives.append((source, target))
                
    # load positives from here
    # this file is generated by the scripts/find_trainingPairs.py
    # it is all the combinations of featured/good -> featured/good
    with open("featured->featured_good_only_positives.csv") as f:
        for line in f:
            splitted = line.split()
            source = splitted[0]
            target = splitted[1]
            
            positives.append((source, target))
        
    # shuffle all lists
    random.shuffle(positives)
    random.shuffle(negatives)

    len_pos = len(positives)
    print("len_pos: " + str(len_pos))
    len_neg = len(negatives)
    print("len_neg: " + str(len_neg))
    if  len_pos > len_neg:
        # too many in positives
        positives = positives[:len_neg]
    else:
        # too many negatives
        negatives = negatives[:len_pos]
    
    for source, target in positives:
        training_data_file.write("{} {} 1\n".format(source, target))

    for source, target in negatives:
        training_data_file.write("{} {} 0\n".format(source, target))