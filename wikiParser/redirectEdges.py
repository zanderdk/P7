# -*- coding: utf-8 -*-
import sys
import xml.etree.cElementTree as etree
import json

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

def createEdge(edge):
    global session
    global counter
    query = """
            MATCH (a:Page)
            WHERE a.title = {title}
            WITH a
            MATCH (b:Page)
            WHERE b.title = {redirectTo}
            CREATE (a)-[:redirect]->(b)
            """
    session.run(query, {'title':edge['title'], 'redirectTo':edge['redirect'] })
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    counter += 1

prefix = "{http://www.mediawiki.org/xml/export-0.10/}"
i = 1
for event, elem in etree.iterparse(sys.stdin):
    if(event == "end"):
        tag = elem.tag.replace(prefix, "")
        if(tag == "page"):
            if i % 10000 == 0:
                print(str(i))
            i += 1
            root = elem

            redirect = root.find("./" + prefix + "redirect") 
            if redirect is not None:
                redirect = redirect.get("title").replace(" ", "_")
            else:
                elem.clear()
                continue
            
            title = root.find("./" + prefix + "title").text.replace(" ", "_")
            obj = {'title': title, 'redirect': redirect}
            createEdge(obj)
            elem.clear()
        elif tag == "record":
            break
