from bs4 import BeautifulSoup
import requests
from random import shuffle


r = requests.get('https://en.wikipedia.org/wiki/Wikipedia:Featured_articles')
html = r.text

def is_featured_article(tag):
    return tag.name == "span" and tag.has_attr("class") and "featured_article_metadata" in tag["class"]

soup = BeautifulSoup(html, "html.parser")
all = soup.find_all(is_featured_article)
all = [x.a["title"] for x in all]

#seed = 0
shuffle(all, lambda: 0)

# take first 100
for x in all[:100]:
  print(x)
