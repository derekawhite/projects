import time
import os

size = 9
grid  = [[]]
pattern = []

def pgrid():
    for i in range (0, size*size):
        print ( f"[{grid[i][0]}]",end=' ')
        if i%3 == 2: print ("", end = ' ')
        if i%size == size-1: print ("")
        if i%(size*3) == size*3-1: print ("")
    print("\n\n")

def loadpatterns():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "killerpattern.txt")) as f:
        return eval(f.read())
    
def initgrid():
    grid=[]
    for i in range (0, size*size):
        grid+= [[0]]
        for j in range (0, len(pattern)):
            if [int(i/size)+1,i%size+1] in pattern[j]:
                grid[i] += [pattern[j]]

    return grid

def rule1 (row, col, val):
    if len(grid[row*size+col]) <= 1:
        return True
    
    pattern = grid[row*size+col][1]
    #print (pattern)
    sum = 0
    for i in range(0, len(pattern)-1): 
        val = grid[(pattern[i][0]-1)*size + (pattern[i][1]-1)][0]
        if val == 0:
            return True
        sum+= val

    if sum != pattern[len(pattern)-1]:
        return False
    
    for i in range(0, len(pattern)-1):
        val1 = grid[(pattern[i][0]-1)*size + (pattern[i][1]-1)][0]
        for j in range (i+1, len(pattern)-1):
            val2 = grid[(pattern[j][0]-1)*size + (pattern[j][1]-1)][0]
            if val1 == val2:
                return False
    return True
         
def rule2 (row, col, val):
    for i in range (0, size):
        if i != col and grid[row * size + i][0] == val:
            return False
        
    for i in range (0, size):
        if i != row and grid[i * size + col][0] == val:
            return False
               
    for i in range (int(row/3)*3, int(row/3)*3+3):
        for j in range (int(col/3)*3, int(col/3)*3+3):
            if [i,j] != [row,col]:
                if grid[i * size + j][0] == val:
                    return False

    return True

def rules(i, val):
    row = int(i / size)
    col = i % size
    return rule2(row, col, val) and rule1(row, col, val)

patterns = loadpatterns()

for pattern in patterns:

    grid = initgrid()
    i = 0
    tic = time.perf_counter()
    count = 0

    while i >= 0 and i < size * size:
        count += 1
        found = False
        foundval = 0

        for value in range(1, 10):
            if grid[i][0] != 0 and grid[i][0] >= value:
                continue
            grid[i][0] = value    
            if rules(i, value):
                    found = True
                    foundval = value
                    break
            
        grid[i][0] = foundval if found else 0
        i = i + 1 if found else i - 1
        if count % 100000 == 0:
            print("{:,}".format(count), i)

    print ("Impossible!") if i < 0 else pgrid()
    print(f"Completed in {time.perf_counter() - tic:0.4f} seconds. Tries = {count}")
    input("Enter to continue: ")