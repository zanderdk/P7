# -*- coding: utf-8 -*-
import sys
import xml.etree.cElementTree as etree
import json

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()

i = 1
with open("2016_02_en_clickstream.tsv", "rt") as clickStream:
    global session
    for x in clickStream:
        cols = x.split()
        source = cols[0]
        target = cols[1]
        amount = cols[2]
        pst = cols[3]
        query = """
            MATCH (a:Page {title:{title1}}),(b:Page {title:{title2}})
            CREATE (a)-[r:clickStream {clicks: {amount}, clickRate: {rate}}]->(b)
            RETURN r
        """
        session.run(query, {"title1": source, "title2": target, "amount":int(amount), "rate": float(pst)})
        if i % 100000 == 0:
            session.close()
            session = driver.session()
        i += 1


