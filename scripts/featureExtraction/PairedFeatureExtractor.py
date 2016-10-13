from neo4j.v1 import GraphDatabase, basic_auth

class PairedFeatureExtractor:

    def __init__(self, maxPathSteps=200):
        self.driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
        self.session = None
        self.maxPathSteps = maxPathSteps

    def _commonTerms(self, fromLink, toLink):
        query = "CALL commonTerms({fromLink}, {toLink})"
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink 
        }
        # res = self.session.run(query, nameMapping)
        # for record in res:
        #     return record[0]
        return 0

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
        return 0 

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
        return 0  

    def _shortestPath(self, fromLink, toLink):
        query = "CALL weightedShortestPath({fromLink}, {toLink}, {maxSteps})"
        nameMapping = {
            "fromLink": fromLink, 
            "toLink": toLink,
            "maxSteps": self.maxPathSteps
        }
        res = self.session.run(query, nameMapping)
        for record in res:
            return record[0]
        return 0  

    def extractFeatures(self, fromArticle, toArticle):
        self.session = self.driver.session()
        path = self._shortestPath(fromArticle, toArticle)
        parents = self._commonParents(fromArticle, toArticle)
        children = self._commonChildren(fromArticle, toArticle)
        terms = self._commonTerms(fromArticle, toArticle)
        self.session.close()
        return (path, parents, children, terms)
