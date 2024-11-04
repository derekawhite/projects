import random
import time

start = 1
end  = 60
num = 10
found = 0

startt = time.time()
for i in range (1, 1000000000):
    r = random.sample(range(start, end +1 ), num)
    if sorted(r) == r:
        found +=1
        print( f"Tries: {i:,} Found: {found:,} Average:{i/found:,.0f} {r}")
    if ( i % 1000000 == 0):
        print(f"{i:,} Time: {(time.time() - startt)/60:,.1f} minutes");









