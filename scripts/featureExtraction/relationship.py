import runQuery

class RelationshipGetter:
    def __init__(self, QueryHelper):

        print("so far so good")

        self._qhelper = QueryHelper

        self._prevFrom = {"name": "", "outgoing": [], "incoming": []}
        self._prevTo = {"name": "", "outgoing": [], "incoming": []}

    def _callGetRelationships(self, title):
        return self._qhelper.runQuery("CALL getRelationships({title})", {"title": title})

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

        # division by zero check
        return inter/union if union != 0 else 0

    def getSuccessorJaccard(self, dict, fromLink, toLink):
        value = self._getJaccard(fromLink, toLink, "outgoing")
        dict["successorJaccard"] = value
 
    def getPredecessorJaccard(self, dict, fromLink, toLink):
        value = self._getJaccard(fromLink, toLink, "incoming")
        dict["predecessorJaccard"] = value