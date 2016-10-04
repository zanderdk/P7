import wikipedia

with open('../list_of_featured_articles', 'r', encoding='utf8') as f:
  titles = f.read().split('\n')

for title in titles:
  print(title)
  article = wikipedia.page(title)

  with open('articles/' + article.title, 'w', encoding='utf8') as f:
    # remove some sections, todo: unsafe
    content = article.content
    content = content[:content.find('== Notes ==')]
    content = content[:content.find('== References ==')]
    content = content[:content.find('== External links ==')]
    f.write(content)

  with open('links/' + article.title, 'w', encoding='utf8') as f:
    f.write("\n".join(article.links))
