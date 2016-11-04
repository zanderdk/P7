import getNgramPairs
import runQuery
from neo4j.v1 import GraphDatabase, basic_auth

qh = runQuery.QueryHelper(GraphDatabase.driver("bolt://localhost:10001", auth=basic_auth("neo4j", "12345")))
finder = getNgramPairs.pairFinder(qh)

all_featured_res = qh.runQuery("match (a:Page) WHERE NOT exists(a.redirect) AND exists(a.featured) return a.title as title", {})
all_featured = []
for record in all_featured_res:
    all_featured.append(record["title"])

print("Got all featured articles")

with open("positives", "w", encoding="utf-8") as positives:
    with open("negatives", "w", encoding="utf-8") as negatives:
        for title in all_featured:
            res = finder.getPairsFromArticle(title)
            for article in res[1]:
                positives.write(title + " " + article + "\n")
            for article in res[2]:
                negatives.write(title + " " + article + "\n")
            print("Done with article: %s" % title)


finder.stopSession()
