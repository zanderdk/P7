from neo4j.v1 import GraphDatabase, basic_auth

class PairedFeatureExtractor:

    def __init__(self, pathLimit=8, keywordLimit=100):
        self.driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
        self.pathLimit = pathLimit
        self.keywordLimit = keywordLimit

    def _runQuery(self, query, mapping):
        with self.driver.session() as session:
            # Return the first element of record stream, do nothing if stream is empty
            for record in session.run(query, mapping):
                return record

        # Returns None if db doesnt return a result
        # Need to check if this ever happens, as it requires handling when calling the func
        # Temp fix: Wrap None in a list...
        return [None]

    def _compareKeywords(self, fromLink, toLink):
        query = '''
            MATCH (a:Page),(b:Page)
            WHERE a.title = {fromLink} AND b.title = {toLink}
            AND exists (a.text) AND exists (b.text)
            CALL keywordSimilarity(a,b,{keywordLimit}) yield similarity as x
            RETURN x'''
        nameMapping = {
            "fromLink": fromLink,
            "toLink": toLink,
            "keywordLimit": self.keywordLimit
        }
        return self._runQuery(query, nameMapping)[0]

    def _commonNeighbors(self, fromLink, toLink):
        query = "CALL common({fromLink},{toLink})"
        nameMapping = {"fromLink": fromLink, "toLink": toLink}
        res = self._runQuery(query, nameMapping)
        # Special case handling needed if exception handling is added to embedded Java
        return (res[0], res[1])

    def _shortestPath(self, fromLink, toLink):
        query = "CALL weightedShortestPathCost({fromLink}, {toLink}, {pathLimit})"
        nameMapping = {
            "fromLink": fromLink,
            "toLink": toLink,
            "pathLimit": self.pathLimit
        }
        return self._runQuery(query, nameMapping)[0]

    def _comparePageViews(self, fromLink, toLink):
        query = '''
            MATCH (a:Page),(b:Page)
            WHERE a.title = {fromLink} AND b.title = {toLink}
            return a.viewCount, b.viewCount'''
        nameMapping = {
            "fromLink": fromLink,
            "toLink": toLink
        }
        res = self._runQuery(query, nameMapping)
        # Handle cases where either page does not have a specified viewCount
        if res[0] is None or res[1] is None:
            return None
        # Cast needed as pageViews are stored as strings in the db..
        return float(res[0]) / float(res[1])

    def extractFeatures(self, fromArticle, toArticle):
        pathWeight = self._shortestPath(fromArticle, toArticle)
        incoming, outgoing = self._commonNeighbors(fromArticle, toArticle)
        keywordSimilarity = self._compareKeywords(fromArticle, toArticle)
        pageViewsRatio = self._comparePageViews(fromArticle, toArticle)
        return (pathWeight, outgoing, incoming, keywordSimilarity, pageViewsRatio)
