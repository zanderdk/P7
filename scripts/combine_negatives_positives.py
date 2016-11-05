counter = 0

def make_format(open_file, label):
    for line in open_file:
            cols = line.split()
            trainingPairs.write("{} {} {}\n".format(cols[0], cols[1], label))
            global counter
            counter += 1

with open("trainingPairs_python", "w", encoding="utf-8") as trainingPairs:
    with open("../negatives", "r", encoding="utf-8") as neg:
        make_format(neg, "0")
    with open("../positives", "r", encoding="utf-8") as pos:
        make_format(pos, "1")


print(counter)