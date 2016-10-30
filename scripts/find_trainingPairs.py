import sys
import random

dict = {}
length = 0
all = []
res = []

for line in sys.stdin:
    rows = line.split()
    source = rows[0]
    target = rows[1]
    all.append(source)
    all.append(target)
    if source not in dict:
        dict[source] = [target]
    else:
        dict[source].append(target)
    length += 1
    res.append((source, target, 1))

all = list(set(all))
allLen = len(all) - 1

def checkAB(a, b):
    if a == b:
        return False
    return False if a not in dict else b in dict[a]

all_set = set(all)
c = []
i = 0
for source in dict.keys():
     not_linked_to = list(all_set - set(dict[source]))
     random.shuffle(not_linked_to)
     # TODO: maybe change 10 as it does not generate enough negative samples
     for target in not_linked_to[:10]:
         c.append((source, target, 0))

random.shuffle(c)
c = c[:length]
res = res + c
random.shuffle(res)
# i = 0
# j = 0
# while i < length:
#     index1 = random.randint(0, allLen)
#     index2 = random.randint(0, allLen)
#     a = all[index1]
#     b = all[index2]
#     if(not checkAB(a, b)):
#         j +=1
#         print(j)
#         continue
#     i += 1
#     if(i % 100 == 0):
#         print(i)
#     res.append((a, b, 0))

for source,target,label in res:
    print(source + "\t" + target + "\t" + str(label))
    