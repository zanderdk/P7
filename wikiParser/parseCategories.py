# Usage: bzcat article_categories_en.ttl.bz2 | python3 parseCategories.py
# -*- coding: utf-8 -*-

import sys
import re
import io
from neo4j.v1 import GraphDatabase, basic_auth

turtle = re.compile(r'<http:\/\/dbpedia.org\/resource\/(.+?)>\s<.*?>\s<http:\/\/dbpedia.org\/resource\/Category:(.+?)>')

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

def createRelation(relation):
    global session
    global counter
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))

    # create category and/or relationship if they don't exist
    session.run("MATCH (p:Page {title:{article}}) MERGE (c:Category {name:{category}}) MERGE (p)-[r:IN_CATEGORY]->(c)", relation)

    counter += 1

for line in sys.stdin:
  if line.startswith('#'):
    continue

  m = turtle.match(line)

  if (m == None):
    print("Error parsing line:", line)
    continue


  createRelation({ 'article': m.group(1), 'category': m.group(2) })

session.close()
print('done.')
