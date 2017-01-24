import runQuery
from neo4j.v1 import GraphDatabase, basic_auth

def getTitleMatches(nGrams):
	qh = runQuery.QueryHelper(GraphDatabase.driver("bolt://localhost:10001", encrypted=False, auth=basic_auth("neo4j", "12345")))

	result = []

	for gram in nGrams:
		mapping = {"title": gram}
		query = "MATCH (a:Page) where (a.title = {title} or a.lower_cased_title = {title}) return a.title"

		queryRes = qh.runQuery(query, mapping)

		if queryRes[0] is not None:
			result.append(queryRes[0]["a.title"])

	return result


