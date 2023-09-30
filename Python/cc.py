#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org filedate
import filedate
import shutil
import sys
import os
import glob
import fnmatch

def setfiledate(destfilename, date, destattribute):
    cmd = f"filedate.File(destfilename).set ({destattribute}=date)"               
    print(f"Setting {destattribute} date of {destfilename} to {date}")
    exec (cmd)

def setfiledatefromsource(destfilename, srcfilename, destattribute, srcattribute):
    cmd = f"filedate.File(destfilename).set ({destattribute}=filedate.File(srcfilename).get().get(srcattribute))"               
    print(f"Setting {destattribute} date of {destfilename} to {filedate.File(srcfilename).get().get(srcattribute)}")
    exec (cmd)
        
def copywithdate(src, dest):
    dest = shutil.copy (src, dest)
    setfiledatefromsource(dest, src, "created", "created")
    setfiledatefromsource(dest, src, "modified", "modified")

def copywithdateresetall(src, dest):
    dest = shutil.copy (src,dest)
    setfiledatefromsource(dest, src, "created", "created")
    setfiledatefromsource(dest, src, "modified", "created")

def copydir(src, dest, dir):
    print (f"copydir {src} {dest} {dir}")
    copyfiles(os.path.join(src, "*"), os.path.join(dest, dir))
    
def copyfiles(src, dest):
    print (f"copyfiles {src} {dest}")
    files =  glob.glob(src)
    for src in files:
        copyfile(src, dest)
    


def copyfile(src, dest):
    if os.path.isdir(src):
        if recurse == True:
            copydir(src, dest, os.path.basename(src))
    else:
        if not os.path.isfile(src):
            print (f"{src} does not exist")
        else:
            print (f"Check dir exists {os.path.dirname(dest)}")
            if not os.path.exists(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
        print (f"copyfile {src}, {dest}")
        copywithdate(src, dest)

srcfiles = ""
dest = ""
initialise = False
recurse = False
folders = []
files = []

for i in range (1, len(sys.argv)):
    if sys.argv[i] == "-i":
        initialise = True
    elif sys.argv[i] == "-r":
        recurse = True
    elif srcfiles == "":
        srcfiles = sys.argv[i]
    elif dest == "":
        dest = sys.argv[i]

if recurse:
    srcdir = ""
    if os.path.isdir(srcfiles):
        srcdir = srcfiles
        pattern = "*"
    elif os.path.isdir(os.path.dirname(srcfiles)):
        srcdir = os.path.dirname(srcfiles)
        pattern = os.path.basename(srcfiles)
    if srcdir != "":
        for (dirpath, dirnames, filenames) in os.walk(srcdir):
            foundfiles = []
            for filename in fnmatch.filter(filenames, pattern):
                foundfiles.append(filename)
            folders.append(dirpath)
            files.append(foundfiles)

    for index in range(0, len(folders)):
        if index < len(files) and len(files[index])>0:
            print(folders[index], files[index])

        
    exit()


if dest == "":
    dest = os.getcwd()
    
print (f"srcfiles={srcfiles} dest={dest}")
if srcfiles != "":
    copyfiles(srcfiles, dest)
else:
    print ( "cc source <destination> <options>")
