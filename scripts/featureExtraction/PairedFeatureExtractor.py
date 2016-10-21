from neo4j.v1 import GraphDatabase, basic_auth
import word2vec

class PairedFeatureExtractor:
    def __init__(self, wantedFeatures, pathLimit=8):
        self.driver = GraphDatabase.driver("bolt://192.38.56.57:10001", auth=basic_auth("neo4j", "12345"))
        # self.word2vec = word2vec.word2vec()
        self.pathLimit = pathLimit
        self.wantedFeatures = wantedFeatures
        self.feature_function_dict = { # if None, then it is special cased
            "pathWeight": lambda dict, articleA, articleB : self._shortestPath(dict, articleA, articleB),
            "keywords": lambda dict, articleA, articleB : self._getKeywords(dict, articleA, articlesB),
            "categories": lambda dict, articleA, articleB : self._getCategories(dict, articleA, articleB),
            "word2vec":  lambda dict, articleA, articleB : self.word2vec.extractWord2vec(dict, articleA, articleB),
            "predecessorJaccard": lambda dict, articleA, articleB : self._getPredecessorJaccard(dict, articleA, articleB),
            "successorJaccard": lambda dict, articleA, articleB : self._getSuccessorJaccard(dict, articleA, articleB)
        }

        self._prevFrom = {"name": "", "outgoing": [], "incoming": []}
        self._prevTo = {"name": "", "outgoing": [], "incoming": []}

    def featureTofieldNames(feature):
        dict = {
            "pathWeight": ["pathWeight"],
            "keywords": ["keywordsA", "keywordsB"],
            "categories": ["categoriesA", "categoriesB"],
            "word2vecSimilarity": ["word2vecSimilarity"],
            "word2vecBuckets": ["word2vec_b0", "word2vec_b1", "word2vec_b2", "word2vec_b3", "word2vec_b4", "word2vec_b5", "word2vec_b6", "word2vec_b7", "word2vec_b8", "word2vec_b9"],
            "predecessorJaccard": ["predecessorJaccard"],
            "successorJaccard": ["successorJaccard"]
        }
        return dict[feature]
        
    def _runQuery(self, query, mapping):
        result = []
        with self.driver.session() as session:

            for record in session.run(query, mapping):
                result.append(record)

        # Returns [None] if db doesnt return a result
        # Need to check if this ever happens, as it requires handling when calling the func
        # Temp fix: Wrap None in a list...
        return [None] if not result else result


    def _getKeywords(self, dict, articleA, articleB):
        query = '''
            MATCH (a:Page)
            WHERE a.title = {article}
            AND exists (a.text)
            CALL keywords(a) yield keyword as x
            RETURN x'''
        nameMapping = {
            "article": article
        }
        keywordsA = self._runQuery(query, nameMapping)
        dict["keywordsA"]

    def _getCategories(self, article):
        query = '''
            MATCH (a:Page)-[:IN_CATEGORY]->(c:Category)
            WHERE a.title = {article}
            RETURN c'''
        nameMapping = {
            "article": article
        }
        return self._runQuery(query, nameMapping)[0]

    def _callGetRelationships(self, title):
        return self._runQuery("CALL getRelationships({title})", {"title": title})

    def _relationTypeHelper(self, name, relationList):
        outgoing = []
        incoming = []

        for fuble in relationList:
            if fuble[2] == "outgoing":
                outgoing.append(fuble)
            elif fuble[2] == "incoming":
                incoming.append(fuble)

        return {"name": name, "outgoing": outgoing, "incoming": incoming }

    def _getRelationships(self, fromLink=None, toLink=None):
        fromLink = self._prevFrom if fromLink is None else fromLink
        toLink = self._prevTo if toLink is None else toLink
        if not(self._prevFrom["name"] == fromLink):
            result = self._callGetRelationships(fromLink)
            self._prevFrom = self._relationTypeHelper(fromLink, result)

        if not(self._prevTo["name"] == toLink):
            result = self._callGetRelationships(toLink)
            self._prevTo = self._relationTypeHelper(toLink, result)

        return (self._prevFrom, self._prevTo)

    def _getCommonRelationCount(self, fromLink, toLink, direction):
        res = self._getRelationships(fromLink, toLink)

        fromArticle = [link[3] for link in res[0][direction]]
        toArticle = [link[3] for link in res[1][direction]]

        return len(set(fromArticle).intersection(set(toArticle)))

    def _getTotalRelationCount(self, fromLink, toLink, direction):
        res = self._getRelationships(fromLink, toLink)

        fromArticle = [link[3] for link in res[0][direction]]
        toArticle = [link[3] for link in res[1][direction]]

        return len(set(fromArticle).union(set(toArticle)))

    def _getJaccard(self, fromLink, toLink, direction):
        inter = self._getCommonRelationCount(fromLink, toLink, direction)
        union = self._getTotalRelationCount(fromLink, toLink, direction)

        return inter/union if union != 0 else 0

    def _getSuccessorJaccard(self, dict, fromLink, toLink):
        value = self._getJaccard(fromLink, toLink, "outgoing")
        dict["successorJaccard"] = value

    def _getPredecessorJaccard(self, dict, fromLink, toLink):
        value = self._getJaccard(fromLink, toLink, "incoming")
        dict["predecessorJaccard"] = value

    def _shortestPath(self, dict, fromLink, toLink):
        query = "CALL weightedShortestPathCost({fromLink}, {toLink}, {pathLimit})"
        nameMapping = {
            "fromLink": fromLink,
            "toLink": toLink,
            "pathLimit": self.pathLimit
        }
        value = self._runQuery(query, nameMapping)[0]
        dict["pathWeight"] = value

    def get_field_names(self):
        """Returns a list of feature names. Only the wanted features are returned."""
        a = set(self.get_all_field_names())
        b = a.intersection(self.wantedFeatures)
        return list(b)

    def get_all_field_names(self):
        """Returns a list of all feature names."""
        return self.feature_function_dict.keys()

    def extractFeatures(self, articleA, articleB):
        """Returns all extracted features as a dictionary
        """
        res_dict = {}
        # go through each of the features and add them to the resulting dict
        for wantedFeature in self.wantedFeatures:
            # feature_function_dict finds the function that returns the feature. Call it.
            feature_func = self.feature_function_dict[wantedFeature]
            feature_func(res_dict, articleA, articleB)
            
        return res_dict
