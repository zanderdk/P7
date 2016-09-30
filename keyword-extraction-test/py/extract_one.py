import sys
from functools import reduce
from metrics import getscore 
import wikipedia

#article = wikipedia.page("New York")
#article = wikipedia.page("An Experiment on a Bird in the Air Pump")

title = 'New York'

file = open('articles/' + title, 'r', encoding='utf8')
content = file.read()
file.close()

file = open('links/' + title, 'r', encoding='utf8')
links = file.read().split(',,')
file.close()

#import re
#match = re.findall("==(.+?)==([\s\S]+?)==", content)

# remove some sections, todo: unsafe
content = content[:content.find('== Notes ==')]
content = content[:content.find('== References ==')]
content = content[:content.find('== External links ==')]

first_paragraph = content[:content.find('==')]

##### rake
sys.path.insert(0, './RAKE-tutorial')
import rake

rake_object = rake.Rake("SmartStoplist.txt", 5, 3, 2)

keywords = rake_object.run(content)

print('rake score:\n')
for x in keywords:
  print(round(x[1], 2), '\t', x[0])


keyphrases = [k[0] for k in keywords if k[1] >= 4] # more than 4 rake points

##### /rake

# todo get link text
score = getscore(keyphrases, title, links, content, first_paragraph)

# print scores
print(title, '\n')

for x in score:
  print(round(x[1], 2), '\t', x[0])

total = reduce((lambda acc, x: acc + x[1]), score, 0)

print()
print('total:  ', round(total, 2))
print('average:', round(total / len(keyphrases), 2))
