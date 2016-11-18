from bs4 import BeautifulSoup
import requests
from neo4j.v1 import GraphDatabase, basic_auth


r = requests.get('https://en.wikipedia.org/wiki/Wikipedia:Good_articles/all')
html = r.text

prut = []
soup = BeautifulSoup(html, "html.parser")
all = soup.find_all("div", { "class" : "NavContent" })
for x in all:
    for y in x.find_all("a"):
        prut.append(y["title"].replace(" ", "_"))
#print(all)
#all = all.find_all("tr")[2]
#all = all.find("td")
#all = all.find_all("a")
#all = [x["title"].replace(" ", "_") for x in all[:-3]]
#print(prut)
#print(len(prut))

# add to db
driver = GraphDatabase.driver("bolt://localhost:10001", auth=basic_auth("neo4j", "12345"))

session = driver.session()
counter = 1

def checkMissingFeatures(titlelist):
    global session
    global counter
    query = """
          MATCH (a:Page {featured: true}) return a.title
          """
    result = session.run(query)

    print(list(set(titlelist)-set(result)))


def setGoodFlag(title):
    global session
    global counter
    query = """
            MATCH (a:Page {title: {title} }) 
            SET a :GoodPage
            """
    session.run(query, {'title':title})
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    counter += 1

for title in prut:
  setGoodFlag(title)
#checkMissingFeatures(all)

session.close()