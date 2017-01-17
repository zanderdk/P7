import getNgramPairs
import runQuery
from neo4j.v1 import GraphDatabase, basic_auth

def getFeaturedOrGood(qh):
    res = qh.runQuery("MATCH (n:FeaturedPage) RETURN n.title UNION ALL MATCH (n:GoodPage) RETURN n.title", {})
    arr = []
    for x in res:
        arr.append(x['n.title'])
    #res.close()
    return arr

qh = runQuery.QueryHelper(GraphDatabase.driver("bolt://localhost:10001", encrypted=False, auth=basic_auth("neo4j", "12345")))
finder = getNgramPairs.pairFinder(qh)

all_featured_res = qh.runQuery("match (a:FeaturedPage) return a.title as title", {})
all_featured = []
for record in all_featured_res:
    all_featured.append(record["title"])

all_featured_len = len(all_featured)
print("Got all featured articles " + str(all_featured_len))

#featuredOrGoodList = set(getFeaturedOrGood(qh))

#print("Got all good and featured articles " + str(len(featuredOrGoodList)))

#with open("positives", "w", encoding="utf-8") as positives:
with open("featured->all_only_negatives.csv", "w", encoding="utf-8") as negatives:
    for i, title in enumerate(all_featured):
        print("Progress: {}/{}".format(i+1,all_featured_len))
        res = finder.getPairsFromArticle(title)
#           for article in res[1]:
#              positives.write(title + " " + article + "\n")
        for article in res[2]:
            negatives.write(title + " " + article + "\n")


finder.stopSession()
