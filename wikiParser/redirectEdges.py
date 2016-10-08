# -*- coding: utf-8 -*-
import sys
import xml.etree.cElementTree as etree
import json

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()

query = """
        match (a:Page),(b:Page) where a.redirect = b.title AND a.redirect <> "None" create (a)-[r:redirect]->(b) RETURN count(r)
        """

session.run(query)

session.close()
