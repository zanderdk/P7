from subprocess import Popen, PIPE

# generate with: mvn package
jar = 'target/wikitext-parser-1.0-SNAPSHOT-jar-with-dependencies.jar'

def toText(title, content):
  p = Popen(['java', '-jar', jar, title], stdin=PIPE, stdout=PIPE, universal_newlines=True)
  # pipe wikitext into process and return stdout
  return p.communicate(content)[0]
