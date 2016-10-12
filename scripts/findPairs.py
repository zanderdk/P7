# Script for creating the dataset for training and testing
# -*- coding: utf-8 -*-
from neo4j.v1 import GraphDatabase, basic_auth
import io

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
session = driver.session()

with io.open("trainingPairs.txt", "w+", encoding="utf-8") as f:
    query = '''
        MATCH (a:Page)-[r:clickStream]->(b:Page) 
        WHERE exists(a.featured) AND a <> b
        RETURN a.title, b.title, r.clickRate'''
    res = session.run(query)
    for record in res:
        line = record[0] + " " + record[1] + " " + str(record[2]) + "\n"
        f.write(line)

session.close()
print("Done")
