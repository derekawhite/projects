import os
import fnmatch
import functools
import filecmp
import sys
import time
import stat
#from PIL import Image

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

def CompareFiles ( f1, f2):

    print ( f"Comparing {f1.path} with {f2.path}" )
    #if f1.ext == ".jpg" and f2.ext == ".jpg":
    #    print ( f"Comparing {f1.path} with {f2.path}" )
    #    image1=Image.open(f1.path)
    #    image2=Image.open(f2.path)
    #    return  list(image1.getdata()) == list(image2.getdata())
    
    return filecmp.cmp(f1.path, f2.path, shallow=False)  

class File:
    def __init__(self, path):
        self.path = path
        self.ext = os.path.splitext(os.path.basename(path))[1]
        file_stats = os.stat(path)

        if self.ext == ".jpg":
            img = Image.open(path)
            self.size = img.entropy()
            print (f"Name = {self.path} Szie = {self.size}")
        else:
            self.size = file_stats.st_size

class Dup:
    def __init__(self, first, second):
        self.first = first
        self.second = second

filepaths1 = []  
filepaths2 = [] 
dups = []   
bDelete = False

if (len(sys.argv) > 3):

    folder1 = sys.argv[1]
    folder2 = sys.argv[2]

    match = sys.argv[3]
    if "-d" in sys.argv:
        bDelete = True

    print (f"Scanning {folder1} {match}")
    for root, dir, files in os.walk(folder1):
        for item in fnmatch.filter(files, match):
            fname = os.path.join(root, item)
            filepaths1.append(File(fname))

    print (f"Found {len(filepaths1)} files")
    print (f"Scanning {folder2} {match}")
    for root, dir, files in os.walk(folder2):
        for item in fnmatch.filter(files, match):
            fname = os.path.join(root, item)
            filepaths2.append(File(fname))
    print (f"Found {len(filepaths2)} files")

    tic = time.perf_counter()

    filepaths1.sort(key=functools.cmp_to_key(sortbysize))
    filepaths2.sort(key=functools.cmp_to_key(sortbysize))


    for i in range (0, len(filepaths1)):
        j = 0        
        if i % 100 == 0:
            print( f"{i} of {len(filepaths1)}", file=sys.stderr)

        while j < len(filepaths2) and filepaths2[j].size < filepaths1[i].size:
            j+=1

        while j < len(filepaths2) and filepaths2[j].size == filepaths1[i].size:
            bMatch = CompareFiles(filepaths1[i],filepaths2[j])
            if bMatch:
                dups.append(Dup(filepaths1[i].path, filepaths2[j].path))
            j += 1

    toc = time.perf_counter()
    dups.sort(key=functools.cmp_to_key(sortbyname))
    for dup in dups:
        print ( f"\"{dup.first}\",\"{dup.second}\"")
        if bDelete and os.path.exists(dup.first):
            os.chmod(dup.first, stat.S_IWRITE)
            print( f"deleting {dup.first}", file=sys.stderr)
            os.remove(dup.first)
            
    print( f"Completed in {toc-tic} seconds", file=sys.stderr)
else:
    print ("dupf <folder1> <folder2> <files> <-d>\ne.g. dup \"E:\\Archive\" \"E:\\My Photographs\" *.mp3")
