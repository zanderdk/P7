#cat pageview* | gzip -cd | python3 this file
import sys

dictionary = {}

for line in sys.stdin:
    try:
        cols = line.split()
        if 'en' == cols[0] and len(cols) == 4:
            if cols[1] in dictionary:
                dictionary[cols[1]] += int(cols[2])
            else:
                dictionary[cols[1]] = int(cols[2])
    except Exception:
        continue

i = 1
with open("../../resources/2016_02_en_clickstream.tsv", "rt") as clickStream:
    for x in clickStream:
        if i > 1:
            cols = x.split()
            source = cols[0]
            linkType = cols[2]
            if source not in dictionary or "link" not in linkType:
                continue
            target = cols[1]
            amount = cols[3]
            Ns = dictionary[source]
            pst = float(amount)/Ns # probabilitySourceTarget
            sys.stdout.write(source + "\t" + target + "\t" + str(amount) + "\t" + str(pst))
            print()
        i += 1

