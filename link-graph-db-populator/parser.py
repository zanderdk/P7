import re
import sys
import fileinput


from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))


regex = re.compile("<(.*?)> <.*?> <(.*?)> \.")
counter = 0
session = driver.session()


def parse(line):
    global session
    if counter % 10000 == 0:
      session.close()
      session = driver.session()
      print("flushed at " + str(counter))
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

for idx, line in enumerate(fileinput.input()):
  counter = idx
  parse(line)
    
# flush the final statements
session.close()
