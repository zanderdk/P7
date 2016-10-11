import wikiextractor

with open('article.txt') as f:
    article = f.read()
    ex = wikiextractor.Extractor()
    res = ex.extract(article)
    print(res)

