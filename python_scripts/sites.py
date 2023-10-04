import json 

with open("tranco.json") as trancoF:
    data = json.load(trancoF)
    total = 0
    for elem in data:
        print(elem, end="")
        print(len(data[elem]))
        total += len(data[elem])

    print(total)