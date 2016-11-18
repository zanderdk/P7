import sys

redirects = set()

with open("redirect_pages.csv", "r", encoding="utf-8") as redirects_pages_file:
  for line in redirects_pages_file:
    redirects.add(line.split()[0])

titles = set()

for line in sys.stdin:
  fromtitle, totitle = line.split()

  titles.add(fromtitle)

  if totitle not in redirects:
    titles.add(totitle)

print('title:ID')
for key in titles:
  print(key)
