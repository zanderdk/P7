import sys

dictionary = {}

for line in sys.stdin:
    currentLine = line.split()
    if 'en' in currentLine[0]:
        if currentLine[1] in dictionary:
            dictionary[currentLine[1]] += int(currentLine[2])
        else:
            dictionary[currentLine[1]] = int(currentLine[2])

print(json.dumps(dictionary, ensure_ascii=False))