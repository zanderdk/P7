from neo4j.v1 import GraphDatabase, basic_auth

class PairedFeatureExtractor:

    def __init__(self, pathLimit=6, keywordLimit=100):
        self.driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
        self.session = None
        self.pathLimit = pathLimit
        self.keywordLimit = keywordLimit

    def _commonTerms(self, fromLink, toLink):
        query = '''
            MATCH (a:Page),(b:Page) 
            WHERE a.title = {fromLink} AND b.title = {toLink}
            CALL keywordSimilarity(a,b,{keywordLimit}) yield similarity as x 
            RETURN x'''
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink,
            "keywordLimit": self.keywordLimit
        }
        res = self.session.run(query, nameMapping)
        for record in res:
            return record[0]
        return None

    def _commonChildren(self, fromLink, toLink):
        query = '''
            MATCH (a:Page)-[r1:clickStream]->(child:Page),(b:Page)-[r2:clickStream]->(child:Page) 
            WHERE a.title = {fromLink} AND b.title = {toLink} AND b <> child
            RETURN count(DISTINCT child)'''
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink 
        }
        res = self.session.run(query, nameMapping)
        for record in res:
            return record[0]
        return None

    def _commonParents(self, fromLink, toLink):
        query = '''
            MATCH (parent:Page)-[r1:clickStream]->(a:Page),(parent:Page)-[r2:clickStream]->(b:Page) 
            WHERE a.title = {fromLink} AND b.title = {toLink} AND a <> parent
            RETURN count(DISTINCT parent)'''
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink 
        }
        res = self.session.run(query, nameMapping)
        for record in res:
            return record[0]
        return None

    def _shortestPath(self, fromLink, toLink):
        query = "CALL weightedShortestPathCost({fromLink}, {toLink}, {pathLimit})"
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink,
            "pathLimit": self.pathLimit
        }
        res = self.session.run(query, nameMapping)
        for record in res:
            return record[0]
        return None

    def _comparePageViews(self, fromLink, toLink):
        query = '''
            MATCH (a:Page),(b:Page) 
            WHERE a.title = {fromLink} AND b.title = {toLink}
            return a.viewCount, b.viewCount'''
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink 
        }
        res = self.session.run(query, nameMapping)
        for record in res:
            if record[0] is None or record[1] is None:
                return None
            return record[0] / record[1]
        return None

    def extractFeatures(self, fromArticle, toArticle):
        self.session = self.driver.session()
        path = self._shortestPath(fromArticle, toArticle)
        parents = self._commonParents(fromArticle, toArticle)
        children = self._commonChildren(fromArticle, toArticle)
        terms = self._commonTerms(fromArticle, toArticle)
        pageViews = self._comparePageViews(fromArticle, toArticle)
        self.session.close()
        return (path, parents, children, terms, pageViews)
