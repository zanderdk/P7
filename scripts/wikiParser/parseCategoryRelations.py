# Usage: bzcat skos_categories_en.ttl.bz2 | python3 parseCategoryRelations.py

import sys
import re
import io
from neo4j.v1 import GraphDatabase, basic_auth

#turtle = re.compile(r'<http:\/\/dbpedia.org\/resource\/Category:(.+?)>\s<.*?#(.+)>\s<.+[#:](.+?)>')
turtle = re.compile(r'<http:\/\/dbpedia.org\/resource\/Category:(.+?)>\s<.*?#(.+?)>\s(.+)')

hashstuff = re.compile(r'.+#(.+?)>')
category = re.compile(r'<http:\/\/dbpedia.org\/resource\/Category:(.+?)>')

driver = GraphDatabase.driver("bolt://localhost:10001", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

def createRelation(args):
  global session
  global counter
  if counter % 10000 == 0:
    session.close()
    session = driver.session()
    print("flushed at " + str(counter))

  # create relationship if it doesn't exist
  session.run("MATCH (c1:Category {name:{category1}}), (c2:Category {name:{category2}}) MERGE (c1)-[r:" + args['relationName'] + "]->(c2)", args)

  counter += 1

def setAttribute(args):
    session.run("MATCH (c:Category {name:{category}}) SET c." + args['attribute'] + " = {value}", args)

for line in sys.stdin:
  if line.startswith('#'):
    continue

  m = turtle.match(line)

  if (m == None):
    print("Error parsing line:", line)
    continue

  cat = m.group(1)
  typ = m.group(2)
  rest = m.group(3)

  if typ == 'broader' or typ == 'related':
    # create BROADER or RELATED relation
    cat2 = category.match(rest).group(1)
    createRelation({ 'category1': cat, 'category2': cat2, 'relationName': typ.upper() })
  elif typ == 'type':
    # set type attribute
    val = hashstuff.match(rest).group(1)
    setAttribute({ 'category': cat, 'attribute': 'type', 'value': val })
  elif typ == 'prefLabel':
    # set label attribute
    val = rest.split('"')[1]
    setAttribute({ 'category': cat, 'attribute': 'label', 'value': val })

session.close()
print('done.')
