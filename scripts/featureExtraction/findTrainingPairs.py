# -*- coding: utf-8 -*-
import sys
import csv
from neo4j.v1 import GraphDatabase, basic_auth

outputColumns = ["source", "target", "click_rate"]

def findTrainingPairs(outputFile):
    driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
    session = driver.session()

    with open(outputFile, "w+", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=" ")
        writer.writerow(outputColumns)   # Write header
        query = '''
            MATCH (a:Page)-[r:clickStream]->(b:Page)
            WHERE exists(a.featured) AND a <> b
            RETURN a.title, b.title, r.clickRate'''
        res = session.run(query)
        for record in res:
            writer.writerow(record.values())

    # Done, close session
    session.close()

if len(sys.argv) > 1:
    findTrainingPairs(sys.argv[1])
    print("Done")
else:
    print("Must specify output file")
