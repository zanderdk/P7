import runQuery
from neo4j.v1 import GraphDatabase, basic_auth
#import getNgrams

class pairFinder:
    def __init__(self):
        self._qh = runQuery.QueryHelper(GraphDatabase.driver("bolt://192.38.56.57:10001", auth=basic_auth("neo4j", "12345")))

    def getPairsFromArticle(self, title):

        mapping = {"title": title}
        query = "MATCH (a:Page) WHERE a.title = {title} Return a.text"

        queryResult = self._qh.runQuery(query, mapping)

        #Result is a list. result[0] is a record. result[0][0] is the actual article text. Don't ask.
        nGrams = getNgrams(queryResult[0][0], 3)

        result = []

        for gram in nGrams:
            if gram not in title:
                mapping = {"title": gram }
                query = "MATCH (a:Page) WHERE a.title = {title} return a.title"
                res = runQuery(query, mapping)
                if res[0] is not None:
                    result.append(res[0])

        return (title, result)