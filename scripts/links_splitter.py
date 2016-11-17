import sys
import random
import math

# load featured articles
featured_articles = set()
with open("featured_articles.csv", "r") as in_featured_articles:
   for line in in_featured_articles:
       featured_articles.add(line.split()[0])

from_is_featured = []
#print(featured_articles)
with open("new_links.csv", "w") as out_new_links:
    #    write header
    out_new_links.write(":START_ID :END_ID\n")
    #    load links.csv
    for line in sys.stdin:
        from_title, to_title = line.split()
        if from_title in featured_articles:
            from_is_featured.append((from_title, to_title))
        else:
            out_new_links.write("{} {}\n".format(from_title, to_title))

# shuffle from_is_featured
random.shuffle(from_is_featured)

# calculate how much should be test, training, regular links
total_count = len(from_is_featured)
print(total_count)
test_count = int(math.floor(total_count*0.20))
print(test_count)
training_count = int(math.floor(total_count*0.40))
rest_count = int(math.floor(total_count*0.40))

# extract test data (20%)
test_data = from_is_featured[:test_count]
print(len(test_data))
# extract training data (40%)
training_data = from_is_featured[test_count:test_count+training_count]
print(len(training_data))

# extract rest data (40%)
walk_data = from_is_featured[test_count+training_count:]
print(len(walk_data))

def write_to_file(file_name, data, header):
    with open(file_name, "w") as out_data:
        if header:
            # write header
            out_data.write(":START_ID :END_ID\n")
        for _from_title, _to_title in data:
            out_data.write("{} {}\n".format(_from_title, _to_title))

write_to_file("test_data.csv", test_data, True)
write_to_file("training_data.csv", training_data, True)
write_to_file("walk_data.csv", walk_data, False)
