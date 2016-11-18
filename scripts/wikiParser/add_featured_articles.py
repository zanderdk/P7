from bs4 import BeautifulSoup
import requests
from neo4j.v1 import GraphDatabase, basic_auth


r = requests.get('https://en.wikipedia.org/wiki/Wikipedia:Featured_articles')
html = r.text

soup = BeautifulSoup(html, "html.parser")
all = soup.find("div", id ="mw-content-text")
all = all.find_all("tr")[2]
all = all.find("td")
all = all.find_all("a")
all = [x["title"].replace(" ", "_") for x in all[:-3]]


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


def setFeatureFlag(title):
    global session
    global counter
    query = """
            MATCH (a:Page {title: {title} }) 
            SET a :FeaturedPage
            """
    session.run(query, {'title':title})
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    counter += 1

for title in all:
    setFeatureFlag(title)
print(len(all))
#checkMissingFeatures(all)

session.close()