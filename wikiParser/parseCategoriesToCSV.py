# Usage: bzcat article_categories_en.ttl.bz2 | python3 parseCategoriesToCSV.py > out.csv
import sys
import re
from neo4j.v1 import GraphDatabase, basic_auth

turtle = re.compile(r'<http:\/\/dbpedia.org\/resource\/(.+?)>\s<.*?>\s<http:\/\/dbpedia.org\/resource\/Category:(.+?)>')

print('article_title,category_name')

for line in sys.stdin:
  if line.startswith('#'):
    continue

  m = turtle.match(line)

  if (m == None):
    print("Error parsing line:", line, file=sys.stderr)
    continue

  #createRelation({ 'article': m.group(1), 'category': m.group(2) })
  print('"' + m.group(1) + '","' + m.group(2) + '"')
