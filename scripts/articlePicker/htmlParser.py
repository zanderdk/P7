from fetch import getPage
from bs4 import BeautifulSoup
import urltools
import os
from stop_words import get_stop_words
from stemming.porter2 import stem
import string

def base(url):
  st = ""
  if(not (url[0:7] == "http://" or url[0:8] == "https://")):
    url = "http://" + url
  i = 0
  for x in url:
    st += x
    if(x == "/"):
      i += 1
      if(i == 3):
        return st[:-1]
  return st

def parseLink(url): #be aware example.com is malformed 
  arr = []
  baseUrl = base(url)
  page = getPage(url)
  if(page is not None):
      soup = BeautifulSoup(page, 'html.parser')
      for x in soup.find_all('a'):
        link = x.get('href')
        if(link is not None and link[0:4] == "http"):
          arr.append(link)
        elif(link is not None and len(link) >= 1 and link[0] == "/"):
          arr.append(baseUrl + link)
        elif(link is not None and link[0:4] == "www."):
          arr.append("http://" + link)
      arr2 = [urltools.normalize(x) for x in arr]
      arr3 = [transform(x) for x in arr2]
      return arr3
  return None

def transform(url):
    if(url[-1] == '/'):
        url = url[:-1]
    url = url.replace("https://www.", "https://")
    url = url.replace("http://www.", "http://")
    return url


