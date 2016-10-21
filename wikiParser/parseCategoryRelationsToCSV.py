# Usage: bzcat skos_categories_en.ttl.bz2 | python3 parseCategoryRelationsToCSV.py > category_relations.csv

import sys
import re

turtle = re.compile(r'<http:\/\/dbpedia.org\/resource\/Category:(.+?)>\s<.*?#(.+?)>\s(.+)')

hashstuff = re.compile(r'.+#(.+?)>')
category = re.compile(r'<http:\/\/dbpedia.org\/resource\/Category:(.+?)>')

# header
print('category1,category2,relationName')

for line in sys.stdin:
  # skip comments
  if line.startswith('#'):
    continue

  m = turtle.match(line)

  if (m == None):
    print("Error parsing line:", line, file=sys.stderr)
    continue

  cat = m.group(1)
  typ = m.group(2)
  rest = m.group(3)

  if typ == 'broader' or typ == 'related':
    # create BROADER or RELATED relation
    cat2 = category.match(rest).group(1)
    #createRelation({ 'category1': cat, 'category2': cat2, 'relationName': typ.upper() })
    print('"' + cat + '","' + cat2 + '",' + typ.upper())
  # TODO: create csv for attributes as well?
  #elif typ == 'type':
    # set type attribute
    #val = hashstuff.match(rest).group(1)
    #setAttribute({ 'category': cat, 'attribute': 'type', 'value': val })
  #elif typ == 'prefLabel':
    # set label attribute
    #val = rest.split('"')[1]
    #setAttribute({ 'category': cat, 'attribute': 'label', 'value': val })
