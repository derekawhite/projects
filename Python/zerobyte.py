import os
import fnmatch
import functools
import time

def sortbysize(item1, item2):
    return 1 if item1.size > item2.size else -1   

class File:
    def __init__(self, path):
        self.path = path
        file_stats = os.stat(path)
        self.size = file_stats.st_size

filepaths = []  
   
for root, dir, files in os.walk(r"e:\My Photographs"):
    for items in fnmatch.filter(files, "*"):
        fname = os.path.join(root, items)
        file = File(fname)
        filepaths.append(file)

print( f"{len(filepaths)} files")
tic = time.perf_counter()
filepaths.sort(key=functools.cmp_to_key(sortbysize))
toc = time.perf_counter()
print(f"Sorted in {toc - tic:0.4f} seconds.")

for i in range (0, len(filepaths) - 1):
    if filepaths[i].size <= 10:
        print ( f"\"{filepaths[i].path}\"")

print(f"Sorted in {toc - tic:0.4f} seconds.")
