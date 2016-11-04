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
	filtered_words = [word for word in text if word not in stops]
	for n in range(1, N+1):
		grams = ngrams(tokenizer.tokenize(text), n)
		for gram in grams:
			gram_as_str = " ".join(gram)
			res.append(gram_as_str)

	return res


def getNgramsOfType(type):
	pass