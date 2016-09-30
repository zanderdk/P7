import wikipedia

titles = ['New York', '7 World Trade Center', 'An Experiment on a Bird in the Air Pump', 'Darjeeling']

for title in titles:
  print(title)
  article = wikipedia.page(title)

  with open('articles/' + article.title, 'w', encoding='utf8') as f:
    f.write(article.content)

  with open('links/' + article.title, 'w', encoding='utf8') as f:
    f.write("\n".join(article.links))
