titles = {}
with open("c:\\temp\\titles.txt") as f:
    for line in f:
        sp = line.split(maxsplit=1)
        if len(sp) == 2 and sp[0].isnumeric():
            titles[int(sp[0])] = sp[1].strip()
print(titles)

print(titles[1], titles[12])