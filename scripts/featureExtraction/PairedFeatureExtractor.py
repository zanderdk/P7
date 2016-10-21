from neo4j.v1 import GraphDatabase, basic_auth
import word2vec
import runQuery
import relationship

class PairedFeatureExtractor:
    def __init__(self, wantedFeatures, pathLimit=8):

        self._qhelper = runQuery.QueryHelper(GraphDatabase.driver("bolt://192.38.56.57:10001", auth=basic_auth("neo4j", "12345")))

        self.relation = relationship.RelationshipGetter(self._qhelper)
        self.word2vec = word2vec.word2vec(self._qhelper)

        self.pathLimit = pathLimit
        self.wantedFeatures = wantedFeatures
        self.feature_function_dict = {
            "pathWeight": lambda dict, articleA, articleB : self._shortestPath(dict, articleA, articleB),
            "keywords": lambda dict, articleA, articleB : self._getKeywords(dict, articleA, articleB),
            "categories": lambda dict, articleA, articleB : self._getCategories(dict, articleA, articleB),
            # TODO: we are calculating the word2Vec similarity twice, stupid
            "word2vecSimilarity":  lambda dict, articleA, articleB : self.word2vec.extractWord2vec(dict, articleA, articleB),
            "word2vecBuckets":  lambda dict, articleA, articleB : self.word2vec.extractWord2vec(dict, articleA, articleB),

            "predecessorJaccard": lambda dict, articleA, articleB : self.relation.getPredecessorJaccard(dict, articleA, articleB),
            "successorJaccard": lambda dict, articleA, articleB : self.relation.getSuccessorJaccard(dict, articleA, articleB)
        }

        self._prevFrom = {"name": "", "outgoing": [], "incoming": []}
        self._prevTo = {"name": "", "outgoing": [], "incoming": []}

    def featureTofieldNames(self, feature):
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

        # TODO: we could probably avoid doing 2 queries by calling keywords procedure on both pages in the same query
        def f(article):
            nameMapping = {"article": article}
            return self._qhelper._runQuery(query, nameMapping)[0]

        
        dict["keywordsA"] = f(articleA)
        dict["keywordsB"] = f(articleB)

    def _getCategories(self, dict, articleA, articleB):
        query = '''
            MATCH (a:Page)-[:IN_CATEGORY]->(c:Category)
            WHERE a.title = {article}
            RETURN c'''

        # TODO: we could probably avoid doing 2 queries by calling keywords procedure on both pages in the same query
        def f(article):
            nameMapping = {"article": article}
            return self._qhelper._runQuery(query, nameMapping)[0]

        dict["categoriesA"] = f(articleA)
        dict["categoriesB"] = f(articleB)

    def _shortestPath(self, dict, fromLink, toLink):
        query = "CALL weightedShortestPathCost({fromLink}, {toLink}, {pathLimit})"
        nameMapping = {
            "fromLink": fromLink,
            "toLink": toLink,
            "pathLimit": self.pathLimit
        }
        value = self._qhelper._runQuery(query, nameMapping)[0]
        dict["pathWeight"] = value

    def get_wanted_feature_names(self):
        """Returns a list of feature names. Only the wanted features are returned."""
        a = set(self.get_all_feature_names())
        b = a.intersection(self.wantedFeatures)
        return list(b)

    def get_all_feature_names(self):
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
