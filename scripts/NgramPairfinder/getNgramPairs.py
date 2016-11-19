import runQuery
from neo4j.v1 import GraphDatabase, basic_auth
import getNgrams
import sys

class pairFinder:
    def __init__(self, qh):
        self._qh = qh

    def stopSession(self):
        self._qh.stopSession()

    def getPairsFromArticle(self, title):
        mapping = {"title": title}
        query = "MATCH (a:Page) WHERE a.title = {title} Return a.text"

        queryResult = self._qh.runQuery(query, mapping)
        print("Got text")

        #Result is a list. result[0] is a record. result[0][0] is the actual article text. Don't ask.
        nGrams = getNgrams.getNgrams(queryResult[0][0], 1)
        print("Got %d grams " % len(nGrams))
        result_neg = []
        result_pos = []

        for gram in nGrams:
            if gram != title:
                mapping = {"fromTitle": title, "title": gram }
                query = '''MATCH (b:Page) WHERE b.title = {title}
                           OPTIONAL MATCH (a:Page)-[r:clickStream]->(b) where a.title = {fromTitle}
                           return b.title as title, count(r) as hasLink'''
                res = self._qh.runQuery(query, mapping)
                if res[0] is not None:
                    res_title = res[0]["title"]
                    res_hasLink = res[0]["hasLink"]
                    if res_hasLink == 1:
                        result_pos.append(res_title)
                    elif res_hasLink == 0:
                        result_neg.append(res_title)
                    else:
                        sys.exit("Found unexpected res_haslink: %s" % res_hasLink)

        return (title, result_pos, result_neg)
        

    
    def getPairsFromArticleThatIsFeaturedOrGood(self, title, allNodes):
        mapping = {"title": title}
        query = "MATCH (a:Page) WHERE a.title = {title} Return a.text"

        # load text from old db that has text
        qh = runQuery.QueryHelper(GraphDatabase.driver("bolt://localhost:10004", encrypted=False, auth=basic_auth("neo4j", "12345")))
        queryResult = qh.runQuery(query, mapping)

        #Result is a list. result[0] is a record. result[0][0] is the actual article text. Don't ask.
        # if no text was found, bail out
        if queryResult[0] is None:
            return (title, [], [])
        nGrams = getNgrams.getNgrams(queryResult[0][0], 5)
        nGrams = list(filter(lambda x: x in allNodes, nGrams))
        result_neg = []
        result_pos = []

        for gram in nGrams:
            if gram != title:
                mapping = {"fromTitle": title, "gram": gram }

                # DOES NOT WORK WITH POSITIVES!!!

                query = '''match (a:FeaturedPage {title:{fromTitle}})
with a as x
match (b:Page {title:{gram}}) where ((b:FeaturedPage) or (b:GoodPage))
with b as y, x as a
optional match (a)-[r:TRAINING_DATA|TEST_DATA|LINKS_TO]->(y) return a.title, y.title, count(r) > 0 as hasLink'''
                res = self._qh.runQuery(query, mapping)
                # the result is None, if gram is not an article that is featured/good
                if res[0] is not None:
                    res_hasLink = res[0]["hasLink"]
                    if not res_hasLink:
                        result_neg.append(gram)

        return (title, result_pos, result_neg)