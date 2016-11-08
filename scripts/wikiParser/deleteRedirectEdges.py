from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
session = driver.session()

query = "MATCH (a:Page)-[r:redirect]->(b:Page) DELETE r"
session.run(query)

session.close()