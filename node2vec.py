import sys
from random import shuffle
from neo4j.v1 import GraphDatabase, basic_auth
from gensim.models import Word2Vec
import networkx as nx
from numpy.linalg import eig
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

color_map = {
        0:'r',
        1:'b',
        2:'m',
        3:'c',
        4:'g',
        5:'yellow',
        6:'brown',
        }

driver = GraphDatabase.driver("bolt://localhost:10001", auth=basic_auth("neo4j", "12345"))

def getAllNodes():
    session = driver.session()
    res = session.run("match (a:Page) WHERE NOT exists(a.redirect) AND (exists(a.good) or exists(a.eatured)) return a.title")
    arr = []
    for x in res:
        arr.append(x['a.title'])
    session.close()
    return arr

def getAllEdges():
        session = driver.session()
        res = session.run("match (a:Page)-[:clickStream]->(b:Page) where not exists(a.redirect) and not exists(b.redirect) return a.title, b.title")
        arr = []
        for x in res:
            arr.append((x['a.title'], x['b.title']))
        session.close()
        return arr

def randomWalk(name):
    session = driver.session()
    query = 'CALL randomWalk({name}, 0.25, 400000, 80, 1, "Page", "title", "clickStream", "None", True, True)'
    res = session.run(query, {"name": name})
    val = ""
    for x in res:
        val = x['walk']
    session.close()
    return val

i = 1

def simulateWalks(r, nodes):
    global i
    walks = []
    session = driver.session()
    for x in range(0, r):
        allNodes = getAllNodes()
        shuffle(allNodes)
        while allNodes:
            walk = randomWalk(allNodes.pop()).split()
            walks.append(walk)
            i += 1
            if(i % 1000 == 0):
                print(i)
    session.close()
    return walks

def makeNodeModel(epoc, r, d, window, workers, nodes):
    walks = simulateWalks(r, nodes)
    model = Word2Vec(walks, size=d, window=window, min_count=5, sg=1, workers=workers, iter=epoc)
    model.save_word2vec_format("./big.bin")
    return model

def findCommunities(model, G):
    X = [model[x] for x in G.nodes()]
    km = KMeans(n_clusters=5, random_state=0).fit(X)

    communities = {}
    for node, cluster in zip(G.nodes(), km.labels_):
        G.node[node]['cluster'] = cluster
        lst = communities.get(cluster, [])
        lst.append(node)
        communities[cluster] = lst

    return G

allNodes = getAllNodes()
print("got nodes")
model = makeNodeModel(1, 20, 128, 10, 8, allNodes)
#model = Word2Vec.load_word2vec_format("./model.bin", binary=True)
#model.save_word2vec_format("test.bin")


#G=nx.Graph()
#G.add_nodes_from(allNodes)
#G.add_edges_from(getAllEdges())

#G = findCommunities(model, G)

#nx.draw_spring(G, node_color=[color_map[G.node[node]['cluster']] for node in G])
#plt.show()
