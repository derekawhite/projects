import os
import fnmatch
import functools
import filecmp
import sys
import time
import stat

def sortbysize(item1, item2):
    if item1.size == item2.size:
        nRet = 1 if item1.path > item2.path else -1 
    else:
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
        file_stats = os.stat(path)
        self.size = file_stats.st_size

class Dup:
    def __init__(self, first, second):
        self.first = first
        self.second = second

filepaths = []  
dups = []   
bDelete = False

if (len(sys.argv) > 2):
    folderindexes =  [i for i, e in enumerate(sys.argv) if e == "-f"]
    folders = []
    folders = [sys.argv[1]]
    for i in folderindexes:
        folders.append(sys.argv[i+1])

    print (folders)

    match = sys.argv[2]
    if "-d" in sys.argv:
        bDelete = True

    tic = time.perf_counter()
    for folder in folders:
        for root, dir, files in os.walk(folder):
            for items in fnmatch.filter(files, match):
                fname = os.path.join(root, items)
                file = File(fname)
                filepaths.append(file)

    toc = time.perf_counter()
    print( f"Scanned folder in {toc-tic} seconds", file=sys.stderr)
    tic = time.perf_counter()

    filepaths.sort(key=functools.cmp_to_key(sortbysize))
    print( f"Found {len(filepaths)} files in {folder}", file=sys.stderr)
    for i in range (0, len(filepaths) - 1):
        if i % 100 == 0:
            print( f"{i} of {len(filepaths)}", file=sys.stderr)
        j = i+1
        while j < len(filepaths) and filepaths[i].size > 0 and filepaths[i].size ==  filepaths[j].size:
            bMatch = CompareFiles(filepaths[i].path,filepaths[j].path)
            if bMatch:
                dups.append(Dup(filepaths[i].path, filepaths[j].path))
            j += 1
    toc = time.perf_counter()
    
    dups.sort(key=functools.cmp_to_key(sortbyname))
    for dup in dups:
        if r"\dups" in dup.first or r"\Archive" in dup.first :
            dup.first,dup.second = dup.second,dup.first

        print ( f"\"{dup.first}\",\"{dup.second}\"")
        if bDelete and os.path.exists(dup.second):
            os.chmod(dup.second, stat.S_IWRITE)
            print( f"deleting {dup.second}", file=sys.stderr)
            os.remove(dup.second)
            
    print( f"Completed in {toc-tic} seconds", file=sys.stderr)
else:
    print ("dup <folder> <files>\ne.g. dup \"c:\\temp\" *.mp3")
