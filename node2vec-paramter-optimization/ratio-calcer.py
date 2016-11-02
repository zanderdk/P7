nums = [0.25, 0.5, 1.0, 2.0, 4.0, 1000]

ratios = []

for num1 in nums:
    for num2 in nums:
        ratios.append(num1/num2)
        ratios.append(num2/num1)


for x in set(ratios):
    print(' options: "' + str(x) + '"')