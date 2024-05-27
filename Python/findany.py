import sys

with open('D:\\temp\\79945\\ndrefs.txt', 'r') as findfile:
    finddata = findfile.read().splitlines()

    with open('D:\\temp\\79945\\vsa_saf_1_20230928_000000_003.log', 'r') as searchfile:
        searchdata = searchfile.read().splitlines()

        for findline in finddata:
            for searchline in searchdata:
                if findline in searchline:
                    print (f"{findline}\n{searchline}\n\n")
