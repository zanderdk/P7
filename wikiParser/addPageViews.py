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
        amount = int(cols[2])
        pst = float(cols[3])
        pageViews = int(round(amount/pst, 0))
        session.run(query, {"title1": source, "title2": target, "amount":int(amount), "rate": float(pst)})
        if i % 100000 == 0:
            session.close()
            session = driver.session()
        i += 1


