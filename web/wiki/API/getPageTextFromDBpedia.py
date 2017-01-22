import requests as rq
from bs4 import BeautifulSoup
from stop_words import get_stop_words
from stemming.porter2 import stem
import string

stop_words = get_stop_words('en')

prefix = "https://en.wikipedia.org/wiki/"

special = "-_,.:%&()\';#!?"
valid = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') | set(special)

translation_table = dict.fromkeys(map(ord, special), None)

def testSpecial(s):
    return set(s).issubset(valid)

def clearHtml(html):
    soup = BeautifulSoup(html.lower(), 'html.parser')
    to_extract = soup.findAll(lambda tag: tag.name == "script" or tag.name == "style")
    for item in to_extract:
        item.extract()
    cleanText = soup.text
    return cleanText

def getPageTextFromDBpedia(title):
	return clearHtml(rq.get(prefix+title).text)

