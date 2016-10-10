# -*- coding: utf-8 -*-
import sys
import xml.etree.cElementTree as etree
import json

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

def deleteEdges():
    global session
    session = driver.session()
    query = """
            match (n:Page)-[r:redirect]->() with r limit 100000 DELETE r
            """
    session.run(query)
    session.close()

for x in range(0, 5):
    deleteEdges()
