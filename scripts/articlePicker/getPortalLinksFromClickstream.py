# This script extracts portalLinks from a clickstream and prints it to stdout
# It assumes the clickstream to be a tab seperated file, in accordance with wikipedia's style (2016-09-29)
# To use it, replace the inputfile with your clickstream file and pipe the result into a new file.

import csv
import sys

inputfile = '2016_03_clickstream.tsv'

with open(inputfile,'r', encoding='utf-8') as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for row in tsvin:
    	if "other" in row[2] and "Main_Page" not in row[0] and "Main_Page" not in row[1]:
    		for item in row:
    			sys.stdout.write(item + "\t")
    		print()
