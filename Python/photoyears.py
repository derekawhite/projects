import os
import fnmatch
import sys
import time
from datetime import datetime
from exif import Image as exifimage
from distutils.dir_util import copy_tree

from PIL import Image

def DateTaken(filename):
    filedate = None
    retval = None
    try:
        img = Image.open(filename)
        filedate = img._getexif()[36867][0:19]

    except:
        image = None

    if (filedate == None):
        filedate = datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y:%m:%d %H:%M:%S')
    try:
        retval = datetime.strptime(filedate, '%Y:%m:%d %H:%M:%S')
        return retval
    except Exception as e:
        print (f"Exception {filename} {filedate} {e} {retval}")

if (len(sys.argv) > 1):

    for i in range(1, len(sys.argv)):
 
        filepaths = []  
        folder = sys.argv[i]
        dirs = []       
        tic = time.perf_counter()

        print (f"Scanning {folder}")
        for it in os.scandir(folder):
            if it.is_dir() and it.name[0].isnumeric():
                dirs.append(it)
        
        for dir in dirs:
            files = []
            for file in os.scandir(dir.path,):
                if file.is_file() and os.path.splitext(file.name)[1].lower() == ".jpg":
                    files.append(file.path)
            years = []
            for file in files:
                d = DateTaken(file)
                if d != None:
                    years.append(DateTaken(file).year)
            year = max(set(years), key = years.count)
            print (year, years)

            target = f"D:\\My Photographs\\Years\\{year}\\{dir.name}"
            print(f"Copy {dir.path} To {target}")
            copy_tree (dir.path, target)

            thsrc = os.path.join(dir.path, '..', 'thumbs', dir.name)
            thdest = os.path.join(target, '..', 'thumbs', dir.name)
            if os.path.exists(thsrc):
                print(f"Copy {thsrc} To {thdest}")
                copy_tree (thsrc, thdest)
            
            
else:
    print ("photoyears <folder1> <folder2> ..")
