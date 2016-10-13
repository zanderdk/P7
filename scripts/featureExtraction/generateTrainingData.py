# Call with path to input file and output file as parameters
import io
import sys
import PairedFeatureExtractor as ext

# Input: File with training pairs on the form:
#       fromTitle toTitle label
# Output: File with training data on the form:
#       shortestPath commonParents commonChildren commonTerms label
def generateTrainingData(inputFile, outputFile):
    with io.open(inputFile, "r", encoding="utf-8") as f:
        with io.open(outputFile, "w+", encoding="utf-8") as outputFile:
            extractor = ext.PairedFeatureExtractor()
            counter = 1
            noPathCounter = 0
            failedCounter = 0
            for line in f:
                entry = line.split()
                features = extractor.extractFeatures(entry[0], entry[1])
                label = entry[2]
                if all(feat is not None for feat in features):
                    if features[0] is 0:
                        noPathCounter += 1
                    line = " ".join([str(x) for x in features]) + " " + label + "\n"
                    outputFile.write(line)
                else:
                    failedCounter += 1
                if counter % 10 is 0:
                    printStatus(counter, failedCounter, noPathCounter)
                counter += 1
            print("Done")
            printStatus(counter - 1, failedCounter, noPathCounter)
            

def printStatus(pairCounter, failedCounter, noPathCounter):
    print("Processed pairs: " + str(pairCounter))
    print("Failed pairs: " + str(failedCounter))
    print("Pairs without path: " + str(noPathCounter) + "\n")

if len(sys.argv) > 2:
    generateTrainingData(sys.argv[1], sys.argv[2])
else:
    print("Must specify input and output files as parameters")
