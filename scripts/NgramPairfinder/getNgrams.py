from nltk import ngrams
from nltk.tokenize import RegexpTokenizer
from funcy import cat
from nltk.corpus import stopwords

tokenizer = RegexpTokenizer(r'\w+')
stops = set(stopwords.words("english"))
def getNgrams(text, N):
	"""
	Calculates N-gram for every 1, 2, ... N. N included.
	Returns a list of strings
	"""
	res = []
	# filter stopwords
	tokenized = tokenizer.tokenize(text)
	filtered_words = [word for word in tokenized if word not in stops and len(word) > 4]
	for n in range(1, N+1):
		grams = ngrams(filtered_words, n)
		for gram in grams:
			gram_as_str = "_".join(gram)
			res.append(gram_as_str)

	return list(set(res))


def getNgramsOfType(type):
	pass