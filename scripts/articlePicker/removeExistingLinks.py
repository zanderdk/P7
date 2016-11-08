# This script synchronizes a portalLinks file, with a page link file.
# The pagelink file is piped into the scripted using stdin.
# The pagelink is assumed to follow the style of DBpedia (2016-09-29)
# To use it set the inputfile to your portal links file, and pipe the results into a file.
# The results are written to stdout as a json encoded dictionary

import sys
import csv
import json

inputfile = 'portalLinks.tsv'
dictionary = {}
prefix = "<http://dbpedia.org/resource/"
i = 0


with open(inputfile,'r', encoding='utf-8') as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    
    for row in tsvin:
    	if row[0] not in dictionary:
    		dictionary[row[0]] = [(row[1], row[3])]
    	else:
    		dictionary[row[0]].append((row[1], row[3]))

for line in sys.stdin:
    if (i > 0):
    	y = line.split()
    	arr = [y[0], y[2]]
    	arr = [z.replace(prefix, "")[:-1] for z in arr]

    	if arr[0] in dictionary:
    		if arr[1] in [x for x,y in dictionary[arr[0]]]:
    			for x,y in dictionary[arr[0]]:
    				if x == arr[1]:
    					dictionary[arr[0]].remove((x,y))
    			if not dictionary[arr[0]]:
    				del dictionary[arr[0]]
    i = 1

print(json.dumps(dictionary, ensure_ascii=False))

