import subprocess
import re
from os import listdir
from os.path import isfile, join

path = 'articles'
onlyfiles = [f for f in listdir(path) if (isfile(join(path, f)) and not f.startswith('.'))]

for title in onlyfiles:
  print(title)

  with open('articles/' + title, 'r', encoding='utf8') as f:
    content = f.read()

  output = subprocess.run(
    "java -Xmx1024m -jar maui/maui-standalone-1.1-SNAPSHOT.jar run \"articles/" + title + "\" -m maui/keyword_extraction_model -v none -n 16"
    , shell=True, stdout=subprocess.PIPE, universal_newlines=True)

  # todo use weights?
  keyphrases = re.findall('Keyword: (.+?) \d+', output.stdout)

  with open('keywords/' + title, 'w', encoding='utf8') as f:
    f.write("\n".join(keyphrases))
