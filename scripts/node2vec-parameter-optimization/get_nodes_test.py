from node2vec import getAllNodes
import time
import pickle

start = time.time()
nodes = getAllNodes()
end = time.time()
print("getAllNodes time:")
print(end - start)

print("nodes length before pickle: %d" % len(nodes))

start = time.time()
with open('all_nodes.pickle', 'w') as f:
    pickle.dump(nodes, f)
end = time.time()
print("pickle dump time:")
print(end - start)

start = time.time()
with open('all_nodes.pickle', 'r') as f:
    nodes = pickle.load(f)
end = time.time()
print("pickle load time:")
print(end - start)

print("nodes length after pickle: %d" % len(nodes))