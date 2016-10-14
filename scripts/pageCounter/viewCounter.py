import sys

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

def setViewCount(title, viewCount):
    global session
    global counter
    query = """
            MATCH (a:Page {title: {title} }) 
            SET a.viewCount = {count}
            """
    session.run(query, {'title':title, 'count':viewCount })
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    counter += 1


for line in sys.stdin:
    try:
        cols = line.split()
        title = cols[0]
        amount = int(cols[1])
        setViewCount(title, amount)
    except Exception:
        continue

