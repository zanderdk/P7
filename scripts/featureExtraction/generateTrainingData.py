# Call with path to input file and output file as parameters
import io
import sys
from neo4j.v1 import exceptions
import PairedFeatureExtractor as ext

# Input: File with training pairs on the form:
#       fromTitle toTitle label
# Output: File with training data on the form:
#       ShortestPath commonOutgoing commonIncoming keywordSimilarity pageViewsRatio label
def generateTrainingData(inputFile, outputFile):
    with io.open(inputFile, "r", encoding="utf-8") as f:
        with io.open(outputFile, "w+", encoding="utf-8") as outputFile:
            extractor = ext.PairedFeatureExtractor()
            counter = 1
            noPathCounter = 0
            failedCounter = 0
            for line in f:
                pairEntry = line.split()
                try:
                    features = extractor.extractFeatures(pairEntry[0], pairEntry[1])
                    dataPoint = features + (pairEntry[2],)
                    if all(field is not None for field in dataPoint):
                        if dataPoint[0] is 0:
                            noPathCounter += 1
                        line = " ".join([str(x) for x in dataPoint]) + "\n"
                        outputFile.write(line)
                    else:
                        failedCounter += 1
                    if counter % 10 is 0:
                        printStatus(counter, failedCounter, noPathCounter)
                    counter += 1
                except exceptions.CypherError:
                    failedCounter += 1
                    counter += 1
                    continue
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
