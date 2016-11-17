# bzcat redirects_en.ttl.bz2 | python3 parseRedirectsToCSV.py > redirects.csv
import sys
import re
from neo4j.v1 import GraphDatabase, basic_auth

turtle = re.compile(r'<http:\/\/dbpedia.org\/resource\/(.+)>\s<http:\/\/dbpedia.org\/ontology\/wikiPageRedirects>\s<http:\/\/dbpedia.org\/resource\/(.+)>')

#print('form_title to_title')

shits = set(['User', 'Wikipedia', 'File', 'MediaWiki', 'Template', 'Help', 'Category', 'Portal', 'Book', 'Draft', 'TimedText ', 'Module', 'Gadget', 'Special', 'Media'])  

for line in sys.stdin:
  if line.startswith('#'):
    continue

  m = turtle.match(line)

  if (m == None):
    print("Error parsing line:", line, file=sys.stderr)
    continue

  #print('"' + m.group(1) + '","' + m.group(2) + '"')
  #print(m.group(1) + ' ' + m.group(2))

  #trash
  fromtitle = m.group(1)
  totitle = m.group(2)

  if ':' in fromtitle:
    if fromtitle.split(':')[0] in shits:
      #print(fromtitle + ' ' + totitle)
      continue

  if ':' in totitle:
    if totitle.split(':')[0] in shits:
      #print(fromtitle + ' ' + totitle)
      continue

  #print(fromtitle + ' ' + totitle)
  print(fromtitle)
 
 
    #trash.add(key)
   # print(fromtitle)

  #trash = set(trash)
  #for key in trash:
  #  print(key)
