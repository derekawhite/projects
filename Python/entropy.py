import os
import fnmatch
import functools
import filecmp
import sys
import time
import stat
from PIL import Image

def sortbyentropy(item1, item2):
    if item1.entropy == item2.entropy:
        nRet = 1 if item1.path > item2.path else -1 
    else:
        nRet = 1 if item1.entropy > item2.entropy else -1 
    return nRet

def sortbyname(item1, item2):
    if item1.first == item2.first:
        nRet = 1 if item1.second > item2.second else -1 
    else:
        nRet = 1 if item1.first > item2.first else -1 
    return nRet

class File:
    def __init__(self, path):
        try:
            print(path)
            self.path = path
            self.ext = os.path.splitext(os.path.basename(path))[1]
            file_stats = os.stat(path)
            self.size = file_stats.st_size
            self.entropy = 0

            if self.ext.lower() == ".jpg":

                    img = Image.open(path)
                    self.entropy = img.entropy()
        except:
            print(f"Error opening {path}")

if (len(sys.argv) > 1):
    for i in range(1, len(sys.argv)):
        filepaths = []  
        folder = sys.argv[i]
        match = "*.jpg"
        tic = time.perf_counter()

        print (f"Scanning {folder} {match}")
        for root, dir, files in os.walk(folder):
            for item in fnmatch.filter(files, match):
                fname = os.path.join(root, item)
                if os.stat(fname).st_size > 20000:
                    filepaths.append(File(fname))

        print (f"Found {len(filepaths)} files")

        filepaths.sort(key=functools.cmp_to_key(sortbyentropy))

        outfile = os.path.join ( folder, "entropy.txt")
        with open(outfile, 'w') as f:
            for path in filepaths:
                ent = "{:.15f}".format(path.entropy)
                f.write(f"{ent};{path.path}\n")
            f.close()

    toc = time.perf_counter()
            
    print( f"Completed in {toc-tic} seconds", file=sys.stderr)
else:
    print ("empathy <folder1> <folder2> <files> <-d>\ne.g. dup \"E:\\Archive\" \"E:\\My Photographs\" *.mp3")
