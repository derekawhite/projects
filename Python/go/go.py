import os
import sys
from glob import glob
import subprocess
import time

if len(sys.argv) >=3:
    if sys.argv[2] == "main":
        os.chdir (os.path.join ("c:\\", "devroot", "mainline", "bw-main"))
    elif sys.argv[1] != "gw" and sys.argv[1] != "db" and sys.argv[1] != "logs":
        os.chdir (os.path.join ("d:\\", "devroot", sys.argv[2]))

currpath = os.getcwd()
splitpath = currpath.split(os.path.sep)
basepath = os.path.join("c:\\", "devroot", "mainline", "bw-main");
todir = ""
topath = ""
fnd = ""

if len(sys.argv) >=2:
    todir = sys.argv[1]

if len(splitpath) >= 4 and splitpath[1] == "devroot":
    basepath = os.path.join ( splitpath[0] + "\\", splitpath[1], splitpath[2], splitpath[3])
elif len(splitpath) == 3 and splitpath[1] == "devroot":
    for d in os.listdir(currpath):
        if os.path.isdir(d) and d.startswith("bw"):
            basepath = os.path.join ( splitpath[0] + "\\", splitpath[1], splitpath[2], d)

if todir == "tools":
    topath = os.path.join(basepath, "BankWorld", "BWTools")
elif todir == "out":
    topath = os.path.join(basepath, "build", "bwout", "debug")
elif todir == "outr":
    topath = os.path.join(basepath, "build", "bwout", "release")
elif todir == "build":
    topath = os.path.join(basepath, "buildfiles")
elif todir == "base":
    topath = basepath
elif todir == "logs":
    if 'CR2_DATA' in os.environ:
        topath = os.path.join(os.environ['CR2_DATA'], "logs")
    else:
        topath = os.path.join("C:\\ProgramData\\CR2", "logs")

    if len(sys.argv) >= 3:
        fnd = sys.argv[2]     
        for filename in glob (fR"{topath}\**\*{fnd}*.*", recursive=True):
            print(f"\"{filename}\"")
            process = subprocess.Popen([r"C:\Program Files\TextPad 8\TextPad.exe", filename])  
            time.sleep(1)
        exit(0) 

elif todir == "bin":
    topath = "c:\\Program Files\\CR2\\BankWorld\\bin"
elif todir == "db":
    topath = r"c:\Users\derek.white\Dropbox (CR2)"   
    if len(sys.argv) >= 3:
        ver = list(sys.argv[2].replace('-',''))
        topath = os.path.join(topath, "ProductDesign-Docs-DEV", "BankWorld", "Projects")
        if ( len(ver) == 3):
            topath = os.path.join(topath, f"Release-{ver[0]}-{ver[1]}-{ver[2]}")
        else:
            fnd = sys.argv[2]
elif todir == "gw" and len(sys.argv) >=3:
    topath = os.path.join(basepath, "BankWorldATM", "Gateway", "Gateways", f"*{sys.argv[2]}*")
elif todir == "py":
    topath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print (topath)

f = open("c:\\devroot\\bin\\goto.bat", 'w')
f.write (f"pushd \"{topath}\"\n")
if fnd != "":
    for filename in glob (fR"{topath}\**\BW*{fnd}*.*", recursive=True):
        print(f"\"{filename}\"")
        process = subprocess.Popen([r"C:\Program Files (x86)\Microsoft Office\Office16\winword.exe", filename])

f.close()







