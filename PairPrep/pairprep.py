from neo4j.v1 import GraphDatabase, basic_auth

pageviewFile = "countedPageViews"
driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
session = driver.session()

def getCommonChildren(articleA, articleB):
    global session
    return session.run("MATCH (p1:Page)-[c1:clickStream]->(child:Page),(p2:Page)-[c2:clickStream]->(child) USING INDEX p1:Page(title) USING INDEX p2:Page(title) WHERE p1.title = {from_name} AND p2.title = {to_link} RETURN count(child)", {"from_name": articleA, "to_name": articleB})

def getCommonParents(articleA,articleB):
    global session
    return session.run("MATCH (parent:Page)-[c1:clickStream]->(p1:Page),(parent)-[c2:clickStream]->(p2:Page) USING INDEX p1:Page(title) USING INDEX p2:Page(title) WHERE p1.title = {from_name} AND p2.title = {to_name} RETURN count(parent)", {"from_name": articleA, "to_name": articleB})

def getShortestPath(articleA,articleB):
    global session
    return session.run("MATCH p=ShortestPath((a:Page {title:{from_name})-[:clickStream*0..5]->(b:Page {title:{to_name})) UNWIND extract (x in nodes(p) | x.title) as x RETURN count(x)-1", {"from_name": articleA, "to_name": articleB})

def getPageviews(article):
    #TODO when database has the values
    return 1
        
        
def extractKeywords(article):
    #TODO when we have keyword scripts
    return []
    
def getLinkProbability(articleA, articleB):
    #TODO db call
    return 1.0
    
def termIntersection(keywordsA, keywordsB):
    A = set(keywordsA)
    B = set(keywordsB)
    if len(B) == 0:
        return 0
    return (len(A.intersection(B)) / len(A.union(B)))
    

def prepPair(pair):
    commonChildCount = getCommonChildren(pair[1],pair[2])
    commonParentCount = getCommonParents(pair[1],pair[2])
    shortestPathLen = getShortestPath(pair[1],pair[2])
    pageviewsA = getPageviews(pair[1])
    pageviewsB = getPageviews(pair[2])
    if pageviewsB = 0:
        viewRatio = 10000
    else:
        viewRatio = pageviewsA / pageviewsB
    keywordsA = extractKeywords(pair[1])
    keywordsB = extractKeywords(pair[2])
    terms = termIntersection(keywordsA,keywordsB)
    linkrank = getLinkProbability(pair[1],pair[2])
    
    return (shortestPathLen, commonChildCount, commonParentCount, terms, linkrank)
    
    # Extract their text
    # Run keywordextractor on both texts
    
    
    # 5) Extract pageviews