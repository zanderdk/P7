# Call with path to input file and output file as parameters
import sys
import csv
from neo4j.v1 import exceptions
import PairedFeatureExtractor as ext

# Columns names, in order, used to print the header
outputColumns = ["path", "outgoing", "incoming", "keywords", "pageviews", "click_rate"]

# Input: File with training pairs on the form:
#       fromTitle toTitle label
# Output: File with training data on the form:
#       shortestPath commonOutgoing commonIncoming keywordSimilarity pageViewsRatio label

def generateTrainingData(inputFilePath, outputFilePath):
    with open(inputFilePath, "r", newline="", encoding="utf-8") as inputFile:
        reader = csv.reader(inputFile, delimiter=" ")

        # Check for header, rewind input file, skip header if present
        hasHeader = csv.Sniffer().has_header(inputFile.read(1024))
        inputFile.seek(0)
        if hasHeader:
            print("Skipped header")
            next(reader)

        with open(outputFilePath, "w+", newline="", encoding="utf-8") as outputFile:
            writer = csv.writer(outputFile, delimiter=" ")
            writer.writerow(outputColumns)   # Write header
            extractor = ext.PairedFeatureExtractor()

            # Counters for keeping status
            counter = 1
            noPathCounter = 0
            noneCounter = 0
            exceptionCounter = 0

            # Iterate over all input lines, using the csv reader
            for row in reader:
                try:
                    features = extractor.extractFeatures(row[0], row[1])
                    if all(field is not None for field in features):
                        dataPoint = features + (row[2],)
                        if dataPoint[0] == 0.0:
                            noPathCounter += 1
                        writer.writerow(dataPoint)
                    else:
                        noneCounter += 1
                    if counter % 1000 == 0:
                        printStatus(counter, noneCounter, exceptionCounter, noPathCounter)
                    counter += 1
                except exceptions.CypherError:
                    exceptionCounter += 1
                    counter += 1
                    continue

            # Done, print final status
            print("\nDone! Final status:")
            printStatus(counter - 1, noneCounter, exceptionCounter, noPathCounter)

def printStatus(pairCount, noneCount, exceptionCount, noPathCount):
    failedCount = noneCount + exceptionCount
    print("\nProcessed pairs: " + str(pairCount))
    print("Failed pairs: %d (%d exceptions, %d None)" %(failedCount, exceptionCount, noneCount))
    print("Generated data points: " + str(pairCount - failedCount))
    print("Pairs without path: " + str(noPathCount))

if len(sys.argv) > 2:
    generateTrainingData(sys.argv[1], sys.argv[2])
else:
    print("Must specify input and output files as parameters")
