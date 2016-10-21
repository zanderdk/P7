# Call with path to input file and output file as parameters
import sys
import csv
from neo4j.v1 import exceptions
import PairedFeatureExtractor as ext
import argparse

# Input: File with training pairs on the form:
#       fromTitle toTitle label
# Output: File with training data on the form:
#       as defined in outputColumns

def generateTrainingData(inputFilePath, outputFilePath, extractor, include_label):
    with open(inputFilePath, "r", newline="", encoding="utf-8") as inputFile:
        reader = csv.reader(inputFile, delimiter=" ")

        # Check for header, rewind input file, skip header if present
        hasHeader = csv.Sniffer().has_header(inputFile.read(1024))
        inputFile.seek(0)
        if hasHeader:
            print("Skipped header")
            next(reader)

        with open(outputFilePath, "w+", newline="", encoding="utf-8") as outputFile:
            label_field_name = "clickProbability"

            # the field names are the field names from the extractor, and the clickProbablity
            field_names_unflattened = map(extractor.featureTofieldNames, extractor.get_wanted_feature_names())
            field_names = [item for sublist in field_names_unflattened for item in sublist]
            if include_label:
                field_names += [label_field_name]
       
            writer = csv.DictWriter(outputFile, fieldnames=field_names, dialect="excel")
            
            # Write header
            writer.writeheader()

            # Counters for keeping status
            counter = 1
            noPathCounter = 0
            noneCounter = 0
            exceptionCounter = 0

            # Iterate over all input lines, using the csv reader
            for row in reader:
                try:
                    from_title = row[0]
                    to_title = row[1]
                    label = row[2]
                    features = extractor.extractFeatures(from_title, to_title)
                    if all(fields is not None for fields in features.values()):
                        # add label to features data
                        if include_label:
                            features[label_field_name] = label
                        pathWeight = features.get("pathWeight")
                        if pathWeight is not None and pathWeight == 0.0:
                            noPathCounter += 1
                        writer.writerow(features)
                    else:
                        noneCounter += 1
                    if counter % 1000 == 0:
                        printStatus(counter, noneCounter, exceptionCounter, noPathCounter)
                    counter += 1
                except exceptions.CypherError as e:
                    print("Cypther error({0}): {1}".format(e.errno, e.strerror))
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

# hack instance that is only used to get the list of all field names 
temp_extractor = ext.PairedFeatureExtractor([])

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("inputFile", help="training pairs data file")
parser.add_argument("outputFile", help="location to put the output file")
parser.add_argument("--include-label", action="store_true", help="include the training data label in the output")
parser.add_argument("--features", default=temp_extractor.get_all_feature_names(), nargs="*")

args = parser.parse_args()
extractor = ext.PairedFeatureExtractor(args.features)
# check if the feature is valid
valid_features = extractor.get_all_feature_names()

for wantedFeature in args.features:
  if wantedFeature not in valid_features:
    exit("Invalid feature {0}\nValid features:\n    {1}".format(wantedFeature, "\n    ".join(valid_features)))

generateTrainingData(args.inputFile, args.outputFile, extractor, args.include_label)