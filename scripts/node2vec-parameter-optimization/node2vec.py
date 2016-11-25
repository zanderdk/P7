import sys
from random import shuffle
from neo4j.v1 import GraphDatabase, basic_auth
from gensim.models import Word2Vec
import networkx as nx
from numpy.linalg import eig
from sklearn.cluster import KMeans
from neo4j.v1 import exceptions
import time
import threading
from multiprocessing import Process, Manager

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
    res = session.run("match (a:Page) where ((a:FeaturedPage) or (a:GoodPage)) return a.title")
    arr = []
    for x in res:
        arr.append(x['a.title'])
    session.close()
    return arr

def randomWalk(name, p, q, l, directed, session):
    try:
        query = 'CALL randomWalk({name}, {p}, {q}, {l}, 1, {directed})'
        res = session.run(query, {"name": name, "p": p, "q": q, "l": l, "directed": directed})
        val = ""
        for x in res:
            val = x['walk']
        return val
    except exceptions.ProtocolError:
        return randomWalk(name)

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def worker(p, q, l, directed, lst, dic, pic, log):
    session = driver.session()
    walks = []
    for node in lst:
        walk = randomWalk(node, p, q, l, directed, session).split()
        walks.append(walk)
    session.close()
    dic[pic] = walks


def simulateWalks(r, nodes, p, q, l, directed, save, log):
    allNodes = []
    threads = 16
    for x in range(0, r):
        allNodes += nodes

    data = chunkIt(nodes, threads)
    manager = Manager()
    returnDics = manager.dict()
    thrs = [Process(target=worker, args=(p, q, l, directed, data[x], returnDics, x, log)) for x in range(0, threads)]
    for x in thrs:
        x.start()
    for x in thrs:
        x.join()
    walks = []
    for i in range(0, threads):
        walks += returnDics[i]

    return walks

def makeNodeModel(p, q, l, r, d, window, directed, workers, nodes, log_file, save = False):
    start = time.time()
    walks = simulateWalks(r, nodes, p, q, l, directed, save, log_file)
    end = time.time()
    print("Simulate walks took: " + str(end - start) + " seconds")
    log_file.write("Simulate walks took: " + str(end - start) + " seconds\n")
    log_file.flush()
    shuffle(walks)

    # this takes a long time, find something else
    #print("Total number of nodes in walks" + str(len(sum(walks, []))))

    start = time.time()
    log_file.write("Starting word2vec...\n")
    log_file.flush()
    model = Word2Vec(walks, size=d, window=window, min_count=0, sg=1, workers=workers, iter=1)
    end = time.time()
    print("Word2Vec call took: " + str(end - start) + " seconds")
    log_file.write("Word2Vec call took: " + str(end - start) + " seconds\n")
    log_file.flush()
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

# only run when not imported
if __name__ == "__main__":
    # find all nodes in the graph
    session = driver.session()
    res = session.run("match (a:Page) WHERE NOT exists(a.redirect) return a.title")
    nodes = []
    for x in res:
        nodes.append(x['a.title'])
    session.close()
    print("got nodes")
    model = makeNodeModel(1, 0.0625, 80, 1, 128, 10, True, 8, nodes)
#model = Word2Vec.load_word2vec_format("./model.bin", binary=True)
    model.save_word2vec_format("test.bin")


#G=nx.Graph()
#G.add_nodes_from(allNodes)
#G.add_edges_from(getAllEdges())

#G = findCommunities(model, G)

#nx.draw_spring(G, node_color=[color_map[G.node[node]['cluster']] for node in G])
#plt.show()


