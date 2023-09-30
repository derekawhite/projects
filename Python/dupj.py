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

#def CompareFiles ( f1, f2):
#    print ( f"Comparing {f1.path} with {f2.path}" )
#    image1=Image.open(f1.path)
#    image2=Image.open(f2.path)
#    return  list(image1.getdata()) == list(image2.getdata())

class File:
    def __init__(self, line):
        spl = line.split(';')
        self.entropy = spl[0].strip()
        self.path = spl[1].strip()

class Dup:
    def __init__(self, first, second):
        self.first = first
        self.second = second

filepaths1 = []  
filepaths2 = [] 
dups = []   
bDelete = False

if (len(sys.argv) > 1):
    entropy1 = []
    entropy2 = []

    tic = time.perf_counter()
    infile1 = os.path.join ( sys.argv[1], "entropy.txt")
    infile2 = ""
    if (len(sys.argv) > 2):
        infile2 = os.path.join ( sys.argv[2], "entropy.txt")

    if "-d" in sys.argv:
        bDelete = True

    if os.path.exists(infile1):
        print (f"Reading {infile1}")
        with open(infile1, 'r') as f:
            entropy1 = f.readlines()  
            f.close()
            print (f"Found {len(entropy1)} files")
    else:
       print (f"File {infile1} Not Found")
       exit(0)


    if infile2 != "":
        if os.path.exists(infile2):
            print (f"Reading {infile2}")
            with open(infile2, 'r') as f:
                entropy2 = f.readlines()  
                f.close()
                print (f"Found {len(entropy2)} files")
        else:
            print (f"File {infile2} Not Found")

    j = 0
    for line1 in entropy1:
        jstart = j
        file1 = File (line1)
        file2 = File (entropy2[j])

        while j < len(entropy2) - 1 and file2.entropy < file1.entropy:
            j+=1
            file2 = File (entropy2[j])

        while j < len(entropy2) - 1 and file1.entropy == file2.entropy:

#            bMatch = CompareFiles(file1, file2)

#            if bMatch:
            dups.append(Dup(file1.path, file2.path))
            j += 1
            file2 = File (entropy2[j])
            
        j = jstart

    toc = time.perf_counter()
    dups.sort(key=functools.cmp_to_key(sortbyname))
    for dup in dups:
        print (f"{dup.first} {dup.second}")
    for dup in dups:
        if bDelete and os.path.exists(dup.first):
            os.chmod(dup.first, stat.S_IWRITE)
            print( f"deleting {dup.first}", file=sys.stderr)
            os.remove(dup.first)
            
    print( f"Completed in {toc-tic} seconds", file=sys.stderr)
else:
    print ("dupf <folder1> <folder2> <files> <-d>\ne.g. dup \"E:\\Archive\" \"E:\\My Photographs\" *.mp3")
