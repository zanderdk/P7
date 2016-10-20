import pandas
from sklearn import preprocessing
from gensim.models import Word2Vec
from neo4j.v1 import GraphDatabase, basic_auth

import matplotlib.pyplot as plt
import seaborn as sns

class word2vec:
    def __init__(self):
        self.model = Word2Vec.load("/home/sw705e16/resources/en_1000_no_stem/en.model", encoding="latin1")
        # self.model = Word2Vec.load_word2vec_format("/home/zander/word2vec/GoogleNews-vectors-negative300.bin", binary=True)

    def getKeywords(self, title):
        driver = GraphDatabase.driver("bolt://127.0.0.1:10001", auth=basic_auth("neo4j", "12345"))
        session = driver.session()
        query = """MATCH (a:Page)
                WHERE a.title = {title}
                AND exists (a.text)
                CALL words(a) yield words as x
                RETURN x"""
        arr = []
        for x in session.run(query, {'title': title}):
            arr.append(x[0])
        
        return sum([x.split() for x in arr], [])

    def compareKeywordSets(self, w1, w2):
        set1 = self.getKeywords(w1)
        set2 = self.getKeywords(w2)
        set1 = list(set([x for x in set1 if x in model.vocab]))
        set2 = list(set([x for x in set2 if x in model.vocab]))
        if not set1 or not set2:
            return None
        return self.model.n_similarity(set1, set2)

