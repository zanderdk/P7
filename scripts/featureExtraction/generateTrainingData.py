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
            for line in f:
                entry = line.split()
                features = extractor.extractFeatures(entry[0], entry[1])
                label = entry[2]
                if all(feat is not None for feat in features):
                    line = " ".join([str(x) for x in features]) + "\n"
                    outputFile.write(line)
                if counter % 1000 is 0:
                    print(counter)
                counter += 1

if len(sys.argv) > 2:
    generateTrainingData(sys.argv[1], sys.argv[2])
else:
    print("Must specify input and output files as parameters")
