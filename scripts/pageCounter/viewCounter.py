import sys

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

def setViewCount(title, viewCount):
    global session
    global counter
    query = """
            MATCH (a:Page) 
            WHERE a.title = {title}
            SET a.viewCount = {count}
            RETURN a.viewCount
            """
    session.run(query, {'title':title, 'count':viewCount })
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    counter += 1


dictionary = {}

for line in sys.stdin:
    try:
        cols = line.split()
        if 'en' == cols[0] and len(cols) == 4:
            if cols[1] in dictionary:
                dictionary[cols[1]] += int(cols[2])
            else:
                dictionary[cols[1]] = int(cols[2])
    except Exception:
        continue


for x,y in dictionary.items():
   setViewCount(x,y)
