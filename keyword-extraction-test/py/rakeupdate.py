from os import listdir
from os.path import isfile, join

# hacks
import sys
sys.path.insert(0, './RAKE-tutorial')
import rake

path = 'articles'
onlyfiles = [f for f in listdir(path) if (isfile(join(path, f)) and not f.startswith('.'))]

for title in onlyfiles:
  print(title)

  with open('articles/' + title, 'r', encoding='utf8') as f:
    content = f.read()

  rake_object = rake.Rake("SmartStoplist.txt", 5, 3, 2)

  keywords = rake_object.run(content)

  #print('rake score:\n')
  #for x in keywords:
  #  print(round(x[1], 2), '\t', x[0])

  #keyphrases = [k[0] for k in keywords if k[1] >= 4] # more than 4 rake points
  keyphrases = [k[0] for k in keywords] 
  keyphrases = keyphrases[:16] # 16 best

  with open('keywords/' + title, 'w', encoding='utf8') as f:
    f.write("\n".join(keyphrases))
