import sys
from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://sw705e16.cs.aau.dk:10001", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

def getNotLinkedTitle(from_title):
  global counter
  if counter % 10000 == 0:
    session.close()
    session = driver.session()
    print("flushed at " + str(counter))

  title = None 
  while title == None:
    #res = session.run("match (a:FeaturedPage {title: '" + from_title + "'}),(b:Page) where id(b) = toInteger(Rand()*11159211) AND NOT (a)-[:LINKS_TO|TRAINING_DATA|TEST_DATA|REDIRECTS_TO]->(b) return b.title")
    res = session.run("match (a:FeaturedPage {title: '" + from_title +"'}),(b:Page) where id(b) = toInteger(Rand()*11159211) AND NOT (a)-[:LINKS_TO|:TRAINING_DATA|TEST_DATA]->(b) AND NOT (a)-[:LINKS_TO]->()-[:REDIRECTS_TO]->(b) return b.title")
    for r in res:
      title = r[0]
  
  return title

for line in sys.stdin:
  featured_title = line.split()[0]
  #print(featured_title)
  to_title = getNotLinkedTitle(featured_title)
  print(featured_title + ' ' + to_title)
