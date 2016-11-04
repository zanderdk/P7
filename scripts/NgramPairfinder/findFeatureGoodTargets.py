import runQuery
from neo4j.v1 import GraphDatabase, basic_auth

qh = runQuery.QueryHelper(GraphDatabase.driver("bolt://localhost:10001", auth=basic_auth("neo4j", "12345")))

all_featured_good_res = qh.runQuery("""
	match (a:Page) WHERE 
	NOT exists(a.redirect) 
	AND (exists(a.good) 
	OR exists(a.featured)) 
	return a.title""", {})
all_featured_good = []
for record in all_featured_good_res:
    all_featured_good.append(record["title"])

counter = 0
all_featured_good = set(all_featured_good)

print("Got all featured articles")
with open("negatives","r",encoding="utf-8") as negatives:
	for line in negatives:
		words = line.split(" ")
		if words[1] in all_featured_good:
			counter += 1

print(counter)