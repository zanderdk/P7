import re
import sys
import csv
import io

# input: pipe compressed edges in + title list + outputfile
# output: writes to outpufile

regex = re.compile("<(.*?)> <.*?> <(.*?)> \.")
prefix = "http://dbpedia.org/resource/"
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

def findTitles(inputFilePath):
    with open(inputFilePath, "r", newline="", encoding="utf-8") as inputFile:
        reader = csv.reader(inputFile, delimiter=" ")

        articles = {}
        for row in reader:
            articles[row[0]] = True

        return articles

lines_in_edges = 170625372.0
counter = 1
edge_counter = 0

if len(sys.argv) > 2:
    titleDict = findTitles(sys.argv[1])
    with open(sys.argv[2], "w+", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=" ")
        for line in sys.stdin:
            if line[0] == "#":
                counter += 1
                continue
            re_res = regex.match(line)
            if re_res is None:
                sys.exit("Error parsing line: " + line)
            from_title = re_res.group(1).replace(prefix, "")
            to_title = re_res.group(2).replace(prefix, "")
            titles = (from_title, to_title)
            if from_title in titleDict and to_title in titleDict:
                writer.writerow(titles)
                edge_counter += 1
            if counter % 1000000 == 0:
                print("Lines parsed: " + str(counter))
                print("Edges found: " + str(edge_counter))
                print("Progress: " + str(round((counter / lines_in_edges) * 100, 2)) + "%\n")
            counter += 1
        print("Done!")
        print("Lines parsed: " + str(counter))
        print("Edges found: " + str(edge_counter))

else:
    print("Give me input")
