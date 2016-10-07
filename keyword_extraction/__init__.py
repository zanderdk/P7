from .rakelib import rake

from subprocess import Popen, PIPE
from os import path

pkgPath = path.dirname(__file__)

# generate with: mvn package
jarPath = path.join(pkgPath, '../wikitext-parser/target/wikitext-parser-1.0-SNAPSHOT-jar-with-dependencies.jar')
stoplistPath = path.join(pkgPath, 'rakelib/SmartStoplist.txt')

def fromText (text):
  # todo relative path?
  rake_object = rake.Rake(stoplistPath, 5, 3, 2)

  keywords = rake_object.run(text)

  #keyphrases = [k[0] for k in keywords if k[1] >= 4] # more than 4 rake points
  keyphrases = [k[0] for k in keywords] 

  return keyphrases[:10] # 10 best

def fromWikitext(wikitext, title):
  p = Popen(['java', '-jar', jarPath, title], stdin=PIPE, stdout=PIPE, universal_newlines=True)
  # pipe wikitext into process and return stdout
  text = p.communicate(wikitext)[0]
  
  return fromText(text)
