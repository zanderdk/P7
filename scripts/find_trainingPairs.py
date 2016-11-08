from neo4j.v1 import GraphDatabase, basic_auth
import random
import sys

driver = GraphDatabase.driver("bolt://192.38.56.57:10001", auth=basic_auth("neo4j", "12345"))

def getAllPositiveTrainingDataNodes():
    session = driver.session()
    res = session.run("match (a:Page)-[r:clickStream]->(b:Page) where exists(a.featured) AND  NOT exists(r.testData) return a.title,b.title")
    arr = []
    for x in res:
        source = x['a.title']
        target = x['b.title']
        arr.append((source, target))
    session.close()
    return arr


with open("training_data.csv", "w") as training_data:
    # positives
    # we make sure this is not test data
    training_data_positive_nodes = getAllPositiveTrainingDataNodes()
    print("Got positive nodes")
    for source, target in training_data_positive_nodes:
        training_data.write("{} {} 1\n".format(source, target))

    # negatives
    # the negatives are derived from the ngram from featured -> all other
    # we need to make sure that no test data is included here
    with open("negatives.csv") as negatives:
        with open("test_data.csv") as test_data:
            test_data_negatives = {}
            for line in test_data:
                splitted = line.split()
                label = splitted[2]
                # only load negatives from test_data
                if label == "0":
                    source = splitted[0]
                    target = splitted[1]
                    if not source in test_data_negatives:
                        test_data_negatives[source] = {}
                    test_data_negatives[source][target] = 1

            training_data_negatives = []
            for line in negatives:
                splitted = line.split()
                # make sure not to include test data in the training data
                source = splitted[0]
                target = splitted[1]
                label = "0"
                if source in test_data_negatives and target in test_data_negatives[source]:
                    # do not add to training data because it is test data 
                    continue
                else:
                    training_data_negatives.append((source, target))
            
            random.shuffle(training_data_negatives)

            len_pos = len(training_data_positive_nodes)
            len_neg = len(training_data_negatives)
            print("len_pos: " + str(len_pos))
            print("len_neg: " + str(len_neg))
            if  len_pos > len_neg:
                # too many in positives
                exit("FATAL ERROR: it is unexpected that there are more positive sample")
            else:
                # too many negatives
                training_data_negatives = training_data_negatives[:len_pos]

            for source, target in training_data_negatives:
                training_data.write("{} {} 0\n".format(source, target))