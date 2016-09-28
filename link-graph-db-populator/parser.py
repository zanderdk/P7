import re
import sys

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "1234"))



regex = re.compile("<(.*?)> <.*?> <(.*?)> \.")

def parse(line):
    session = driver.session()
    if line[0] == '#':
        # do not process comments
        return
    re_res = regex.match(line)
    if re_res is None:
        sys.exit("error parsing line: " + line)
    else:
        from_link = re_res.group(1)
        to_link = re_res.group(2)
        session.run("CREATE (a:Link {name:{from_name}}) -[:LinksTo]-> (b:Link {name:{to_name}})", {"from_name": from_link, 
                                                           "to_name": to_link})
        session.close()


with open("/home/simon/page_links_en.ttl") as fileobject:
  for line in fileobject:
    parse(line)
    
