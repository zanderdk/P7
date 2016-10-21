from py2neo import Graph

print("hej")
graph = Graph(bolt=None, host='192.38.56.57', bolt_port=10001, user='neo4j', password='12345')

cursor=graph.run("MATCH (n) RETURN n")
for n in cursor:
    print(n)