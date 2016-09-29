# This script suggests candidates for link-checking.
# It takes a json encoded python dictionary (InputDictInJson) of portallinks and sorts them according to popularity.
# the pick() functions removes and returns the most popular portallink as a pair of articles.
# To make the script check pairs against live wikipedia for already fixed links, set doLiveCheck to true.
# Without modification the script returns the 20 most popular pairs.


import sys
import csv
import json
import requests
import urltools
from bs4 import BeautifulSoup
from htmlParser import parseLink
import time

wikiPrefix = "https://en.wikipedia.org/wiki/"
timeout = int(time.time())
sortedList = []
jsonString = ""
doLiveCheck = False
InputDictInJson = 'resultsInJson'

with open(InputDictInJson,'r', encoding='utf-8') as jsonFile:
    jsonString = jsonFile.read()

dictio = json.loads(jsonString)
    
toBeSorted = []
for x,y in dictio.items():
    for z in y:
        toBeSorted.append((int(z[1]), x, z[0]))

sortedList = sorted(toBeSorted, key=lambda tup: tup[0])

def pick():
    global timeout
    pair = sortedList.pop()
    if doLiveCheck:
        while(time.time() < 3 + timeout): #This should be moved to fetch
            pass
        timeout = time.time()
        links = parseLink(wikiPrefix + pair[1])

        for link in links:
            if pair[2] in urltools.normalize(link):
                return pick()
    return pair


[print(pick()) for x in range(0, 20)]
