import sys
from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost:10001", auth=basic_auth("neo4j", "12345"))

session = driver.session()

def getNotLinkedTitle(from_title):
  title = None 
  counter = 0
  while title == None and counter < 10:
    #res = session.run("match (a:FeaturedPage {title: '" + from_title + "'}),(b:Page) where id(b) = toInteger(Rand()*11159211) AND NOT (a)-[:LINKS_TO|TRAINING_DATA|TEST_DATA|REDIRECTS_TO]->(b) return b.title")
    counter += 1
    res = session.run("match (a:FeaturedPage {title: {title}}),(b:Page) where id(b) = toInteger(Rand()*11159211) AND NOT (a)-[:LINKS_TO|TRAINING_DATA|TEST_DATA]->(b) AND NOT (a)-[:LINKS_TO]->()-[:REDIRECTS_TO]->(b) return b.title", {'title': from_title})
    for r in res:
      title = r[0]
    
  return title

for line in sys.stdin:
  featured_title = line.split()[0]
  #print(featured_title)
  to_title = getNotLinkedTitle(featured_title)

  if to_title == None:
    print('#Error, failed getting negative for', featured_title)
  else:
    print(featured_title + ' ' + to_title)
