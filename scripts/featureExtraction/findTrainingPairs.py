# -*- coding: utf-8 -*-
from neo4j.v1 import GraphDatabase, basic_auth
import io
import sys


if len(sys.argv) > 1:
    driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))
    session = driver.session()
    with io.open(sys.argv[1], "w+", encoding="utf-8") as f:
        query = '''
            MATCH (a:Page)-[r:clickStream]->(b:Page) 
            WHERE exists(a.featured) AND a <> b
            RETURN a.title, b.title, r.clickRate'''
        res = session.run(query)
        for record in res:
            line = " ".join([str(val) for val in record.values()]) + "\n"
            f.write(line)
    session.close()
    print("Done")

else:
    print("Must specify output file")
