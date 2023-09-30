import os
import fnmatch
import functools
import filecmp
import sys
import time
import shutil

def sortbyfileandsizename(item1, item2):
    if item1.filename == item2.filename:
        nRet = 1 if item1.size > item2.size else -1 
    else:
        nRet = 1 if item1.filename > item2.filename else -1 
    return nRet

def sortbysize(item1, item2):
    nRet = 1 if item1.size > item2.size else -1 
    return nRet

def sortbyname(item1, item2):
    if item1.first == item2.first:
        nRet = 1 if item1.second > item2.second else -1 
    else:
        nRet = 1 if item1.first > item2.first else -1 
    return nRet

def CompareFiles ( fn1, fn2):
    return filecmp.cmp(fn1, fn2, shallow=False)
      
class File:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        file_stats = os.stat(path)
        self.size = file_stats.st_size

class Undup:
    def __init__(self, first, second, size):
        self.first = first
        self.second = second
        self.size = size
        self.dup = False

filepaths = []  
undups = []   
index = 0

if (len(sys.argv) > 2):
    folder = sys.argv[1]
    match = sys.argv[2]
    
    tic = time.perf_counter()
    for root, dir, files in os.walk(folder):
        for items in fnmatch.filter(files, match):
            fname = os.path.join(root, items)
            file = File(fname)
            filepaths.append(file)

    toc = time.perf_counter()
    print( f"Scanned folder in {toc-tic} seconds", file=sys.stderr)
    tic = time.perf_counter()

    filepaths.sort(key=functools.cmp_to_key(sortbyfileandsizename))
    print( f"Found {len(filepaths)} files in {folder}", file=sys.stderr)
    for i in range (0, len(filepaths) - 1):
        if i % 100 == 0:
            print( f"{i} of {len(filepaths)}", file=sys.stderr)
        j = i+1
        while j < len(filepaths) and filepaths[i].size > 0 and filepaths[i].filename ==  filepaths[j].filename:
            bUnMatch = filepaths[i].size != filepaths[i].size
            if not bUnMatch:
                bUnMatch = not CompareFiles(filepaths[i].path,filepaths[j].path)
            if bUnMatch:
                undup = Undup(filepaths[i].path, filepaths[j].path, filepaths[i].size)
                undups.append(undup)
            j += 1
    toc = time.perf_counter()
    
    undups.sort(key=functools.cmp_to_key(sortbysize))

    for undup in undups:
        index += 1

        ext1 = os.path.splitext(os.path.basename(undup.first))
        ext2 = os.path.splitext(os.path.basename(undup.second))
        dest1 = os.path.join ("c:\\temp", "dups", f"{ext1[0]}__{index}__1{ext1[1]}")
        dest2 = os.path.join ("c:\\temp", "dups", f"{ext2[0]}__{index}__2{ext2[1]}")
        print ( f"\"{undup.first}\",\"{undup.second}\"")
        shutil.copy (undup.first, dest1)
        shutil.copy (undup.second, dest2)

    print( f"Completed in {toc-tic} seconds", file=sys.stderr)
else:
    print ("undup <folder> <files>\ne.g. undup \"c:\\temp\" *.mp3")
