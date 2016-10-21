from neo4j.v1 import GraphDatabase, basic_auth
#import word2vec
import runQuery
import relationship

class PairedFeatureExtractor:
    def __init__(self, wantedFeatures, pathLimit=8):

        self._qhelper = runQuery.QueryHelper(GraphDatabase.driver("bolt://192.38.56.57:10001", auth=basic_auth("neo4j", "12345")))

        self.relation = relationship.RelationshipGetter(self._qhelper)
        # self.word2vec = word2vec.word2vec()

        self.pathLimit = pathLimit
        self.wantedFeatures = wantedFeatures
        self.feature_function_dict = { # if None, then it is special cased
            "pathWeight": lambda dict, articleA, articleB : self._shortestPath(dict, articleA, articleB),
            "keywords": lambda dict, articleA, articleB : self._getKeywords(dict, articleA, articlesB),
            "categories": lambda dict, articleA, articleB : self._getCategories(dict, articleA, articleB),
            "word2vec":  lambda dict, articleA, articleB : self.word2vec.extractWord2vec(dict, articleA, articleB),
            "predecessorJaccard": lambda dict, articleA, articleB : self.relation.getPredecessorJaccard(dict, articleA, articleB),
            "successorJaccard": lambda dict, articleA, articleB : self.relation.getSuccessorJaccard(dict, articleA, articleB)
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
