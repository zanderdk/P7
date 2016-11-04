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
            if gram not in title:
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