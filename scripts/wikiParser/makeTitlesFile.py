import sys

titles = set() 

for line in sys.stdin:
  fromtitle, totitle = line.split()

  titles.add(fromtitle)
  titles.add(totitle)

print('title:ID')
for key in titles:
  print(titles)
  