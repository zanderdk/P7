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
all = [x["title"] for x in all[:-3]]


# add to db
#driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "12345"))

#session = driver.session()
counter = 1

def setFeatureFlag(title):
    global session
    global counter
    query = """
            MATCH (a:Page {title: {title} }) 
            SET a.featured = {featured}
            """
    session.run(query, {'title':title, 'featured':True })
    if counter % 10000 == 0:
        session.close()
        session = driver.session()
        print("flushed at " + str(counter))
    counter += 1

for title in all:
  print(title.replace(" ", "_"))
  #setFeatureFlag(title)
print(len(all))

#session.close()