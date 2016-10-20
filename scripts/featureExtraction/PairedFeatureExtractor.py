from neo4j.v1 import GraphDatabase, basic_auth
import word2vec

class PairedFeatureExtractor:
    def __init__(self, wantedFeatures, pathLimit=8):
        self.driver = GraphDatabase.driver("bolt://192.38.56.57:10001", auth=basic_auth("neo4j", "12345"))
        self.word2vec = word2vec.word2vec()
        self.pathLimit = pathLimit
        self.wantedFeatures = wantedFeatures
        self.feature_function_dict = { # if None, then it is special cased
            "pathWeight": self._shortestPath,
            "keywordsA": None,
            "keywordsB": None,
            "pageViewsA": None,
            "pageViewsB": None,
            "predecessorsA": None,
            "successorsA": None,
            "predecessorsB": None,
            "successorsB": None,
            "word2vec": self.word2vec.compareKeywordSets,
            "PredesccorJaccard": self._getPredesccorJaccard,
            "SucessorJaccard": self._getSucessorJaccard,
        }

        self._prevFrom = {"name": "", "outgoing": [], "incoming": []}
        self._prevTo = {"name": "", "outgoing": [], "incoming": []}

    def _runQuery(self, query, mapping):
        with self.driver.session() as session:

            result = []
            for record in session.run(query, mapping):
                result.append(record)

        # Returns [None] if db doesnt return a result
        # Need to check if this ever happens, as it requires handling when calling the func
        # Temp fix: Wrap None in a list...
        return [None] if not result else result


    def _getKeywords(self, article):
        query = '''
            MATCH (a:Page)
            WHERE a.title = {article}
            AND exists (a.text)
            CALL keywords(a) yield keyword as x
            RETURN x'''
        nameMapping = {
            "article": article
        }
        return self._runQuery(query, nameMapping)[0]


    def _callGetRelationships(self, title):
    	return self._runQuery("CALL getRelationships({title})", {"title": toLink})

    def _relationTypeHelper(self, name, relationList):
   		outgoing = []
   		incoming = []

   		for fuble in relationList:
   			if fuble[2] == "Outgoing":
   				outgoing.append(fuble)
   			elif fuble[2] == "Incoming":
   				incoming.append(fuble)

   		return {"name": name, "outgoing": outgoing, "incoming": incoming }

    def _getRelationships(self, fromLink = self._prevFrom[name], toLink = self._prevTo[name]):
    	if not(self._prevFrom[name] == fromLink):
    		result = self._callGetRelationships(fromLink)
    		self._prevFrom = self._relationTypeHelper(fromLink, result)

    	if not(self._prevTo[name] == toLink):
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
		inter = _getCommonRelationCount(fromLink, toLink, direction)
		union = _getTotalRelationCount(fromLink, toLink, direction)

		return inter/union if union != 0 else 0

	def _getSucessorJaccard(self, fromLink, toLink):
		return _getJaccard(fromLink, toLink, "outgoing")

	def _getPredecessorJaccard(self, fromLink, toLink):
		return _getJaccard(fromLink, toLink, "incoming")




    def _shortestPath(self, fromLink, toLink):
        query = "CALL weightedShortestPathCost({fromLink}, {toLink}, {pathLimit})"
        nameMapping = {
            "fromLink": fromLink,
            "toLink": toLink,
            "pathLimit": self.pathLimit
        }
        return self._runQuery(query, nameMapping)[0]


    def _getPageViews(self, fromLink, toLink):
        query = '''
            MATCH (a:Page),(b:Page)
            WHERE a.title = {fromLink} AND b.title = {toLink}
            return a.viewCount, b.viewCount'''
        nameMapping = { "fromLink": fromLink, "toLink": toLink }
        res = self._runQuery(query, nameMapping)
        # Handle cases where either page does not have a specified viewCount
        if res[0] is None or res[1] is None:
            return None
        # Cast needed as pageViews are stored as strings in the db..
        return (float(res[0]), float(res[1]))

    def get_field_names(self):
        """Returns a list of feature names. Only the wanted features are returned."""
        a = set(self.get_all_field_names())
        b = a.intersection(self.wantedFeatures)
        return list(b)

    def get_all_field_names(self):
        """Returns a list of all feature names."""
        return self.feature_function_dict.keys()

    def extractFeatures(self, fromArticle, toArticle):
        """Returns all extracted features as a dictionary
        """
        res_dict = {}
        # go through each of the features and add them to the resulting dict
        for wantedFeature in self.wantedFeatures:
            # feature_function_dict finds the function that returns the feature. Call it.
            feature_func = self.feature_function_dict[wantedFeature]

            # If it is None, do not do anything, as it is special cased
            if feature_func is not None:
                res_dict[wantedFeature] = feature_func(fromArticle, toArticle)
        
        if "keywordsA" in self.wantedFeature:
            res_dict["keywordsA"] = self._getKeywords(fromArticle)
        if "keywordsB" in self.wantedFeature:
            res_dict["keywordsB"] = self._getKeywords(toArticle)
        
        if "pageViewsA" or "pageViewsB" in self.wantedFeature:
            pagevA, pagevB = self._getPageViews(fromArticle, toArticle)
            if "pageViewsA" in self.wantedFeatures: res_dict["pageViewsA"] = pagevA
            if "pageViewsB" in self.wantedFeatures: res_dict["pageViewsA"] = pagevB
            
        
        # special casing for _getRelationships as it returns a tuple
        if "predecessorsA" or "successorsA" in self.wantedFeatures:
            predecessorsA, successorsA = self._getRelationships(fromArticle)
            if "predecessorsA" in self.wantedFeatures: res_dict["predecessorsA"] = predecessorsA
            if "successorsA" in self.wantedFeatures: res_dict["successorsA"] = successorsA
        if "predecessorsB" or "successorsB" in self.wantedFeatures:
            predecessorsB, successorsB = self._getRelationships(toArticle)
            if "predecessorsB" in self.wantedFeatures: res_dict["predecessorsB"] = predecessorsB
            if "successorsB" in self.wantedFeatures: res_dict["successorsB"] = successorsB

        return res_dict
