# -*- coding: utf-8 -*-
import sys
import xml.etree.cElementTree as etree
import json

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

def createNode(page):
    global session
    global counter
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    session.run("CREATE (a:Page { title:{title}, id:{id}, revisionId:{revisionId}, redirect:{redirect}, text:{text}, timestamp:{timestamp}, restrictions:{restrictions} })", { "title": page['title'], "id":page['id'], "revisionId":page['revisionId'], "redirect":page['redirect'], "text":page['text'], "timestamp":page['timestamp'], 'restrictions':json.dumps(str(page['restrictions']), ensure_ascii=False)  })
    counter += 1

# obj = {'id': id, 'title':title, 'revisionId': revisionId, 'redirect': redirect, 'text':text, 'timestamp': timeStamp, 'restrictions': restrictions}


# linkDic = {}

# i = 0
# with open("2016_02_en_clickstream.tsv", "rt") as clickStream:
#     for x in clickStream:
#         if i > 0:
#             cols = x.split()
#             source = cols[0]
#             target = cols[1]
#             linkType = cols[2]
#             amount = cols[3]
#             if "other" not in linkType:
#                 query = """
#                     MATCH (a:Page {title:{title1}}),(b:Page {title:{title2}})
#                     CREATE (a)-[r:clickStream {clicks: {amount}}]->(b)
#                     RETURN r
#                 """
#                 session.run(query, {"title1": source, "title2": target, "amount":int(amount)})
#         if i % 10000 == 0:
#             session.close()
#             session = driver.session()
#         i += 1
#

prefix = "{http://www.mediawiki.org/xml/export-0.10/}"

for event, elem in etree.iterparse(sys.stdin):
    if(event == "end"):
        tag = elem.tag.replace(prefix, "")
        if(tag == "page"):
            root = elem
            title = root.find("./" + prefix + "title").text.replace(" ", "_")
            id = int(root.find("./" + prefix + "id").text)

            redirect = root.find("./" + prefix + "redirect") 
            if redirect is not None:
                redirect = redirect.get("title")

            revision = root.find("./" + prefix + "revision")
            revisionId =  int(revision.find("./" + prefix + "id").text)
            timeStamp = revision.find("./" + prefix + "timestamp").text

            text = revision.find("./" + prefix + "text").text if redirect is None else None

            restrictions = root.find("./" + prefix + "restrictions")
            if restrictions is not None:
                restrictions = restrictions.text
                if (":" not in restrictions and "=" not in restrictions):
                    restrictions = {'all': restrictions}
                else:
                    restrictions = restrictions.split(":")
                    restrictions = [tuple(x.split("=")) for x in restrictions]
                    restrictions = [(x,y) for x,y in restrictions if y != ""]
                    restrictions = dict(restrictions)
                    restrictions = None if len(restrictions) == 0 else restrictions
            obj = {'id': id, 'title':title, 'revisionId': revisionId, 'redirect': redirect, 'text':text, 'timestamp': timeStamp, 'restrictions': restrictions}
            createNode(obj)
            elem.clear()
        elif tag == "record":
            break
