from neo4j.v1 import GraphDatabase, basic_auth
from datetime import datetime

class PairedFeatureExtractor:

    def __init__(self, pathLimit=5, keywordLimit=100):
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

    def _commonChildren(self, fromLink, toLink):
        query = '''
            MATCH (a:Page)-[r1:clickStream]->(child:Page),(b:Page)-[r2:clickStream]->(child:Page) 
            WHERE a.title = {fromLink} AND b.title = {toLink} AND b <> child
            RETURN count(DISTINCT child)'''
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink 
        }
        self.session = self.driver.session()        
        res = self.session.run(query, nameMapping)
        self.session.close()        
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
        self.session = self.driver.session()        
        res = self.session.run(query, nameMapping)
        self.session.close()        
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
        start = datetime.now()
        path = self._shortestPath(fromArticle, toArticle)
        end = datetime.now()
        duration = end - start
        print("Shortest path: " + str(duration.microseconds/1000))

        start = datetime.now()
        parents = self._commonParents(fromArticle, toArticle)
        end = datetime.now()
        duration = end - start
        print("Common parents : " + str(duration.microseconds/1000))

        start = datetime.now()
        children = self._commonChildren(fromArticle, toArticle)
        end = datetime.now()
        duration = end - start
        print("Common children: " + str(duration.microseconds/1000))

        start = datetime.now()
        terms = self._commonTerms(fromArticle, toArticle)
        end = datetime.now()
        duration = end - start
        print("Common terms: " + str(duration.microseconds/1000))

        start = datetime.now()
        pageViews = self._comparePageViews(fromArticle, toArticle)
        end = datetime.now()
        duration = end - start
        print("Page views: " + str(duration.microseconds/1000) + "\n")

        return (path, parents, children, terms, pageViews)
