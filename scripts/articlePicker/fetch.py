import urllib.robotparser
import requests
import time

def getPage(url):
    try:
      if(not url[0:4] == "http"):
            url = "http://" + url
      headers = {
          'User-Agent': 'awesomeBot', #Find a perfect name for our bot
      }
      page = requests.get(url, headers=headers, timeout=5.00)
      if(page.status_code == requests.codes.ok):
          return page.text
      else:
          return None
    except:
      return None

