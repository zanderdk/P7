from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://192.38.56.57:10001", auth=basic_auth("neo4j", "12345"))

def getAllTestDataNodes():
    session = driver.session()
    res = session.run("match (a:Page)-[r:clickStream]->(b:Page) where r.testData return a.title,b.title")
    arr = []
    for x in res:
        source = x['a.title']
        target = x['b.title']
        arr.append((source, target))
    session.close()
    return arr


with open("test_data.csv", "w") as test_data_out:
    test_data_nodes = getAllTestDataNodes()
    print("Got nodes")
    for source, target in test_data_nodes:
        test_data_out.write("{} {}\n".format(source, target))