import time
googol = pow(10,100)
start = time.time()
gap = 10000000

print
print ("1 googolplex = 1", end='')
for i in range(googol):
    if i % gap == gap - 1:
        now = time.time()
        elapsedseconds = (now - start)
        if ( elapsedseconds > 0):
            persecond = i/elapsedseconds
            togoseconds = (googol - i)/persecond
            togoyears = togoseconds/60/60/24/365
            print (f"\n{i + 1} down, {googol-i - 1} to go. Estimated Completion time {togoyears:.2} years")
        time.sleep(1)




