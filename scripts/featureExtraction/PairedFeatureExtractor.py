from neo4j.v1 import GraphDatabase, basic_auth
from datetime import datetime

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
            AND exists (a.text) AND exists (b.text)
            CALL keywordSimilarity(a,b,{keywordLimit}) yield similarity as x 
            RETURN x'''
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink,
            "keywordLimit": self.keywordLimit
        }
        self.session = self.driver.session()
        res = self.session.run(query, nameMapping)
        self.session.close()
        for record in res:
            return record[0]
        return None

    def _commonChildrenAndParents(self, fromLink, toLink):
        self.session = self.driver.session()        
        res = self.session.run("CALL common({fromLink},{toLink})", {"fromLink": fromLink, "toLink": toLink})
        self.session.close() 
        for record in res:
            return (record[0], record[1])
        return None

    def _shortestPath(self, fromLink, toLink):
        query = "CALL weightedShortestPathCost({fromLink}, {toLink}, {pathLimit})"
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink,
            "pathLimit": self.pathLimit
        }
        self.session = self.driver.session()        
        res = self.session.run(query, nameMapping)
        self.session.close()        
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
        self.session = self.driver.session()        
        res = self.session.run(query, nameMapping)
        self.session.close()        
        for record in res:
            if record[0] is None or record[1] is None:
                return None
            # Cast needed as pageViews are, apparently, stored as strings in the database
            return float(record[0]) / float(record[1])
        return None

    def extractFeatures(self, fromArticle, toArticle):  
        path = self._shortestPath(fromArticle, toArticle)
        common = self._commonChildrenAndParents(fromArticle, toArticle)

        children = common[0]        
        parents = common[1]
        terms = self._commonTerms(fromArticle, toArticle)
  
        pageViews = self._comparePageViews(fromArticle, toArticle)

        return (path, parents, children, terms, pageViews)
