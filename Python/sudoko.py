import time

size = 9
grid  = [[]]
pattern = []

def pgrid():
    for i in range (0, size):
        for j in range (0, size):
            print ( f"[{grid[i][j]}]",end=' ')
            if j%3 == 2:
                print ("", end = ' ')
        if i%3 == 2:
           print ("")

        print ("")
    print ("")        

def rule1 (row, col, val):
    return pattern[row][col] == 0 or pattern[row][col] == val
        
def rule2 (row, col, val):
    if val in grid[row]:
        return False

    for i in range (0, size):
        if grid[i][col] == val:
            return False
                
    for i in range (int(row/3)*3, int(row/3)*3+3):
        for j in range (int(col/3)*3, int(col/3)*3+3):
            if grid[i][j] == val:
                return False
    return True

for i in range(0, size):
    grid[0].append(0)
for i in range(0, size - 1):
    grid.append(grid[0].copy())

pattern.append ([int(st) for st in [*'000050000']])
pattern.append ([int(st) for st in [*'000007901']])
pattern.append ([int(st) for st in [*'007208056']])
pattern.append ([int(st) for st in [*'004000308']])
pattern.append ([int(st) for st in [*'100000200']])
pattern.append ([int(st) for st in [*'023006090']])
pattern.append ([int(st) for st in [*'040960000']])
pattern.append ([int(st) for st in [*'002005000']])
pattern.append ([int(st) for st in [*'096800005']])

print ("Format is (Examples) 000009000, 629534000, 010700000")
#for i in range (0, size):
 #   str = input(f"Enter a row {i+1}: ")
  #  pattern.append([int(st) for st in [*str]])

i = 0
tic = time.perf_counter()

while i >= 0 and i < size * size:
    row = int(i / size)
    col = i % size
    found = False
    foundval = 0
        
    for value in range(1, 10):
        if grid[row][col] != 0 and grid[row][col] >= value:
            continue
            
        if rule1(row, col, value) and rule2(row, col, value):
            found = True
            foundval = value
            break
        
    i = i + 1 if found else i - 1
    grid[row][col] = foundval if found else 0

print ("Impossible!") if i < 0 else pgrid()
toc = time.perf_counter()
print(f"Completed in {toc - tic:0.4f} seconds")
