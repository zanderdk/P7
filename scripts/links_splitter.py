import sys
import random

# load featured articles
featured_articles = set()
with open("featured_articles.csv", "r") as featured_articles:
    for line in featured_articles:
        featured_articles.add(line)

from_is_featured = []

with open("new_links.csv", "w") as out_new_links:
    # write header
    out_new_links.write(":START_ID :END_ID\n")
    # load links.csv
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
test_count = int(total_count*0.20)
training_count = int(total_count*0.40)
rest_count = int(total_count*0.40)

# extract test data (20%)
test_data = from_is_featured[:test_count]

# extract training data (40%)
training_data = from_is_featured[test_count:training_count]

# extract rest data (40%)
rest_data = from_is_featured[training_data:]


def write_to_file(file_name, data):
    with open(file_name, "w") as out_data:
        # write header
        out_data.write(":START_ID :END_ID\n")
        for _from_title, _to_title in data:
            out_data.write("{} {}\n".format(_from_title, _to_title))

write_to_file("test_data.csv", test_data)
write_to_file("training_data.csv", training_data)
write_to_file("rest_links.csv", rest_data)
