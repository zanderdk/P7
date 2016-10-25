import runQuery

class RelationshipGetter:
    def __init__(self, QueryHelper):
        self._qhelper = QueryHelper

        self._prevFrom = {"name": "", "outgoing": [], "incoming": []}
        self._prevTo = {"name": "", "outgoing": [], "incoming": []}

    def _callGetRelationships(self, title):
        return self._qhelper._runQuery("CALL getRelationships({title})", {"title": title})

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

        fromLink = self._prevFrom['name'] if fromLink is None else fromLink
        toLink = self._prevTo['name'] if toLink is None else toLink
        
        if (self._prevFrom["name"] != fromLink):
            result = self._callGetRelationships(fromLink)
            self._prevFrom = self._relationTypeHelper(fromLink, result)

        if (self._prevTo["name"] != toLink):
            result = self._callGetRelationships(toLink)
            self._prevTo = self._relationTypeHelper(toLink, result)

        #Note that this mutates class variables, even though it returns the results as well
        return (self._prevFrom, self._prevTo)

    def _getCommonRelationCount(self, fromLink, toLink, direction):
        #res is a tuble of dictionaries containg relations of fromlink and toLink
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

        print("inter " + str(inter))
        print("union " + str(union))

        # division by zero check
        return inter/union if union != 0 else 0

    def _getBestCommon(self, fromLink, toLink, direction):
        res = self._getRelationships(fromLink, toLink)

        fromArticle = [link for link in res[0][direction]]
        toArticle = [link for link in res[1][direction]]

        ans = []

        for predec in fromArticle:
            for pred in toArticle:
                if pred['otherNode'] == predec['otherNode']:
                    if pred['clickRate'] > predec['clickRate']:
                        ans.append(pred)
                    else:
                        ans.append(predec)
        
        output = sorted(ans, key=lambda pred: pred['clickRate'])
        output.pop()['clickRate']


    def getSuccessorJaccard(self, dict, fromLink, toLink):
        value = self._getJaccard(fromLink, toLink, "outgoing")
        dict["successorJaccard"] = value
 
    def getPredecessorJaccard(self, dict, fromLink, toLink):
        value = self._getJaccard(fromLink, toLink, "incoming")
        dict["predecessorJaccard"] = value

    def getPredecessorCount(self, dict, fromLink, toLink):
        value = self._getCommonRelationCount(fromlink, toLink, "incoming")
        dict["CommonPredecessorCount"] = value

    def getSuccessorCount(self, dict, fromLink, toLink):
        value = self._getCommonRelationCount(fromLink, toLink, "outgoing")
        dict["commonSuccessorCount"] = value

    def getBestPredecessor(self, dict, fromLink, toLink):
        value = self._getBestCommon(fromLink, toLink, "incoming")
        dict["bestCommonPredecessor"] = value

    def getBestSuccessor(self, dict, fromLink, toLink):
        value = self._getBestCommon(fromLink, toLink, "outgoing")
        dict["bestCommonSuccessor"] = value

