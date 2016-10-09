# -*- coding: utf-8 -*-
import sys
import xml.etree.cElementTree as etree
import json

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

def createEdge(page):
    global session
    global counter
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    counter += 1

prefix = "{http://www.mediawiki.org/xml/export-0.10/}"

for event, elem in etree.iterparse(sys.stdin):
    if(event == "end"):
        tag = elem.tag.replace(prefix, "")
        if(tag == "page"):
            root = elem
            title = root.find("./" + prefix + "title").text.replace(" ", "_")

            redirect = root.find("./" + prefix + "redirect") 
            if redirect is not None:
                redirect = redirect.get("title")
            
            if(redirect is not None):
                obj = {'title': title, 'redirect': redirect}
                createEdge(obj)
            elem.clear()
        elif tag == "record":
            break
