# Call with path to input file and output file as parameters
import io
import sys
import PairedFeatureExtractor as ext


def loadPairs(inputFile):
    pairs = []
    with io.open(inputFile, "r", encoding="utf-8") as f:
        for line in f:
            entry = line.split()
            pairs.append((entry[0], entry[1], entry[2]))
    return pairs



# Input: File with training pairs on the form:
#       fromTitle toTitle label
# Output: File with training data on the form:
#       shortestPath commonParents commonChildren commonTerms label
def generateTrainingData(inputList, outputFile):
    with io.open(outputFile, "w+", encoding="utf-8") as outputFile:
        extractor = ext.PairedFeatureExtractor()
        counter = 1
        noPathCounter = 0
        failedCounter = 0
        for pair in inputList:
            features = extractor.extractFeatures(pair[0], pair[1])
            label = pair[2]
            if all(feat is not None for feat in features):
                if features[0] is 0:
                    noPathCounter += 1
                line = " ".join([str(x) for x in features]) + " " + label + "\n"
                outputFile.write(line)
            else:
                failedCounter += 1
            if counter % 100 is 0:
                printStatus(counter, failedCounter, noPathCounter)
            counter += 1
        print("Done")
        printStatus(counter - 1, failedCounter, noPathCounter)
            

def printStatus(pairCounter, failedCounter, noPathCounter):
    print("Processed pairs: " + str(pairCounter))
    print("Failed pairs: " + str(failedCounter))
    print("Pairs without path: " + str(noPathCounter) + "\n")

if len(sys.argv) > 2:
    pairs = loadPairs(sys.argv[1])
    generateTrainingData(pairs, sys.argv[2])
else:
    print("Must specify input and output files as parameters")
