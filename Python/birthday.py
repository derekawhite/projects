import random
import sys

def match(n):
    res = ([random.randrange(1, 366, 1) for i in range(n)])
    return  (len(res) != len(set(res)))

if (len(sys.argv) > 2):
    nPeople = int(sys.argv[2])
else:
    print ("Usage: brithday [nPeople]")
    exit(0)

nTries = 10000 

nMatching = 0 
for i in range(nTries):
    nMatching += 1 if match(nPeople) else 0

print (f"People: {nPeople} Same Birthday: {nMatching/nTries*100:,.2f}%")
