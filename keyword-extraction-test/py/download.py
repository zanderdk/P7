import wikipedia

#article = wikipedia.page("New York")

article = wikipedia.page("Ancestry of the Godwins")

with open('articles/' + article.title, 'w', encoding='utf8') as f:
  f.write(article.content)

with open('links/' + article.title, 'w', encoding='utf8') as f:
  f.write(",,".join(article.links))
