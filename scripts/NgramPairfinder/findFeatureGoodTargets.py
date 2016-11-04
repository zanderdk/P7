import runQuery
from neo4j.v1 import GraphDatabase, basic_auth

qh = runQuery.QueryHelper(GraphDatabase.driver("bolt://localhost:10001", auth=basic_auth("neo4j", "12345")))
finder = getNgramPairs.pairFinder(qh)

all_featured_res = qh.runQuery("match (a:Page) WHERE NOT exists(a.redirect) AND exists(a.featured) return a.title as title", {})
all_featured = []
for record in all_featured_res:
    all_featured.append(record["title"])

counter = 0

print("Got all featured articles")
with open("negatives","r",encoding="utf-8") as negatives:
	for line in negatives:
		words = line.split(" ")
		if words[1] in all_featured:
			counter += 1

print(counter)