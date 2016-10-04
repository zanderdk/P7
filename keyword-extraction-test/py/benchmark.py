import sys
from os import listdir
from os.path import isfile, join
from functools import reduce
from metrics import getscore 

scores = []

path = 'articles'
onlyfiles = [f for f in listdir(path) if (isfile(join(path, f)) and not f.startswith('.'))]

for title in onlyfiles:
  # load
  with open('articles/' + title, 'r', encoding='utf8') as f:
    content = f.read()

  with open('links/' + title, 'r', encoding='utf8') as f:
    links = f.read().split('\n')

  with open('keywords/' + title, 'r', encoding='utf8') as f:
    keyphrases = f.read().split('\n')

  first_paragraph = content[:content.find('==')]

  # todo get link text
  score = getscore(keyphrases, title, links, content, first_paragraph)

  # print scores
  #print(title, '\n')

  total = reduce((lambda acc, x: acc + x[1]), score, 0)

  scores.append(total)
  #print()
  print(title, round(total, 2))
  #print('average:', round(total / len(keyphrases), 2))
  for x in score:
    print('   ', round(x[1], 2), '\t', x[0])


totaltotal = reduce((lambda acc, x: acc + x), scores, 0)

print('\ntotal score:', round(totaltotal, 2))
