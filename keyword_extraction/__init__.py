from .rakelib import rake
import re
import sys

from subprocess import Popen, PIPE
from os import path

pkgPath = path.dirname(__file__)

sys.path.insert(0, path.join(pkgPath, '../custom-wikiextractor'))
import wikiextractor

# generate with: mvn package
jarPath = path.join(pkgPath, '../wikitext-parser/target/wikitext-parser-1.0-SNAPSHOT-jar-with-dependencies.jar')
stoplistPath = path.join(pkgPath, 'rakelib/SmartStoplist.txt')

# result of optimize_rake.py, on test data with wikipedia links as keys.
  # Best result at  2.15
  # with	min_char_length 7
  #       max_words_length 4
  #       min_keyword_frequency 2
rake_object = rake.Rake(stoplistPath, 7, 4, 2)

ex = wikiextractor.Extractor()

def fromText (text):
  keywords = rake_object.run(text)

  #keyphrases = [k[0] for k in keywords if k[1] >= 4] # more than 4 rake points
  keyphrases = [k[0] for k in keywords] 

  return keyphrases[:10] # 10 best

def fromWikitext(wikitext, title):
  #p = Popen(['java', '-jar', jarPath, title], stdin=PIPE, stdout=PIPE, universal_newlines=True)
  # pipe wikitext into process and return stdout
  #text = p.communicate(wikitext)[0]

  text = ex.extract(wikitext)
  text = re.sub('\.(\S)', r'. \1', text) # split punctuation

  return fromText(text)
