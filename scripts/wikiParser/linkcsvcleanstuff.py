shits = set(['User', 'Wikipedia', 'File', 'MediaWiki', 'Template', 'Help', 'Category', 'Portal', 'Book', 'Draft', 'TimedText ', 'Module', 'Gadget', 'Special', 'Media'])

for line in sys.stdin:
  fromtitle, totitle = line.split()

  if ':' in fromtitle:
    if fromtitle.split(':')[0] in shits:
      continue

  if ':' in totitle:
    if totitle.split(':')[0] in shits:
      continue

  if key1 in shits or key2 in shits:
    continue  

  print(fromtitle + ' ' + totitle)
 