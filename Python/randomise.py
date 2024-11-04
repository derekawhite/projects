import random
import time
import math

random.seed()
startt = time.time()
sqrts = 0
maxs = 0
total = 0
num = 100000000

for i in range (1, num):

    r1 =  random.random()
    r2 =  random.random()
    r3 =  random.random()
    r4 =  random.random()

    sqrts += math.sqrt(r1)
    maxs += max(r2, r3)
    total += r4

print (f"Average random         : {total/num} (sqrt: {math.sqrt(total/num)})")
print (f"Average random sqrt    : {sqrts/num}")
print (f"Average random max of 2: {maxs/num}")













