import time

size = 5
grid  = [[]]
values = ['A', 'B', 'C']
values0 = ['A', 'B', 'C', '0']
checkvalues = ['A', 'B', 'C', 'X']

def pgrid():
    for row in grid:
        for col in row:
            if col == 'X':
                print ( f"[ ]",end=' ')
            else:
                print ( f"[{col}]",end=' ')
             
        print ("")
    print ("")        

def rule1 (row, col, val):
    rCnt = 0
    cCnt = 0

    for i in range (0, size):
        if i != row and  grid[i][col] == val:
            rCnt += 1;
            
    for i in range (0, size):
        if i != col and  grid[row][i] == val:
            cCnt += 1
    
    if val in values and (cCnt > 0 or rCnt > 0):
        return False  
    elif val == 'X' and (cCnt > 1 or rCnt > 1):
        return False
        
    return True
    
def rule2 (row, col, val):
    if val in ('0', 'X'):
        return True
    firstinrow = lastinrow = firstincol = lastincol = True
    for i in range (0, col):
        if grid[row][i] in values0:
            firstinrow = False
    for i in range (col + 1, size):
        if grid[row][i] in values0:
            lastinrow = False
    for i in range (0, row):
        if grid[i][col] in values0:
            firstincol = False
    for i in range (row + 1, size):
        if grid[i][col] in values0:
            lastincol = False
         
    if firstincol and top[col] in values and top[col] != val:
        return False
    if lastincol and bottom[col] in values and bottom[col] != val:
        return False
    if firstinrow and left[row] in values and left[row] != val:
        return False
    if lastinrow and right[row] in values and right[row] != val:
        return False
        
    return True

def rule3 (row, col, val):
    if col > 2 and left[row] == val:
        return False
    if col < 2 and right[row] == val:
        return False
    if row > 2 and top[col] == val:
        return False
    if row < 2 and bottom[col] == val:
        return False
    return True


def checkrules (row, col, val):
    r1 = rule1(row, col, val)
    r2 = rule2(row, col, val)
    r3 = rule3(row, col, val)
    return r1 and r2 and r3
    
for i in range(0, size):
    grid[0].append('0')
for i in range(0, size - 1):
    grid.append(grid[0].copy())

#pgrid()
    
i = 0
tic = time.perf_counter()

#print ("Format is (Examples) A-B-C, --AA-, -AB--")
#left = input("Enter a left: ")
#right = input("Enter a right: ")
#top = input("Enter a top: ")
#bottom = input("Enter a bottom: ")
top = '-AAB-'
bottom = 'BCB--'
left = '-BC--'
right = '-CAC-'
  
while i >= 0 and i < size * size:
    row = int(i / size)
    col = i % size

    found = False
    foundval = '0'
        
    for value in checkvalues:

        if grid[row][col] != '0' and grid[row][col] >= value:
            continue
            
        if checkrules(row, col, value):
            found = True
            foundval = value
            break
           
    i = i + 1 if found else i - 1
    grid[row][col] = foundval if found else '0'

print ("Impossible!") if i < 0 else pgrid()
        
toc = time.perf_counter()
print(f"Completed in {toc - tic:0.4f} seconds")
