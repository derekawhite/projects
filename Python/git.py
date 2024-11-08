import re
import os
import sys
import subprocess

def chkout(id):
    print (id)
    if not id.isnumeric():
        return False;

    sub = subbranch
    if sub == "":
        sub = "main"
    if subbranch == "" and basebranch != "":
        sub = basebranch

    for branch in branches:
        if branch[0:2] == "* ":
            branch = branch[2:]

        if id in branch:

            print(f"git checkout {sub}")
            print(f"git pull")
            os.system(f"git checkout {sub}")
            os.system(f"git pull")

            print (f"{branch} {sub}" )
            if branch != sub:
                print(f"git checkout {branch}")
                print (f"git merge {sub}")
                os.system(f"git checkout {branch}")
                os.system(f"git merge {sub}")
                os.system(f"git branch")
            return True;
    return False

os.system('cls')

gitres = subprocess.run(['git', 'branch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
branches = gitres.stdout.decode('utf-8').split('\n')
branches = [x.strip(' ') for x in branches]
stErr = gitres.stderr.decode('utf-8').split('\n')
branchExists  = False
branchCurrent = False

if (len(stErr) > 0 and not stErr[0].startswith("warning") and len(stErr[0]) > 0):
    print (f"git branch returned: \"{stErr}\"")
    exit()

prn = ""
desc = ""
subbranch = ""
fname = "c:\\temp\\gitm.txt"
cherry = ""
doDel = False

splitpath = os.getcwd().split('\\')    
if splitpath[2] in ("550", "551", "552", "553", "554", "555", "556"):
    subbranch = splitpath[2]

if subbranch == "550":
    subbranch = "bw-550-b21"
if subbranch == "551":
    subbranch = "bw-551-b06"
if subbranch == "552":
    subbranch = "bw-552-b01"
if subbranch == "553":
    subbranch = "bw-553-b05"
if subbranch == "554":
    subbranch = "bw-554-b06"
if subbranch == "555":
    subbranch = "bw-555-b01"
if subbranch == "556":
    subbranch = "bw-556-b01"

basepath = "bw-main"
basebranch = "main"
if len(splitpath) >= 4 and splitpath[1] == "devroot":
    basepath = splitpath[3]
    
if basepath == "bw-main":
    basebranch = "main"
else:
    basebranch = basepath

print(f"subbranch = {subbranch}" )
print(f"basebranch = {basebranch}" )

if len(sys.argv) == 2:
    if chkout(sys.argv[1]):
        exit()

if (len(sys.argv) > 1):
    for index, arg in enumerate(sys.argv):
        if index > 0:
            if arg[:2] == "-r":
                with open(fname, 'r') as f:
                    print(f.read())
                    f.close()
                exit()
            elif arg[:2] == "-s":
                subbranch = arg[2:]
                print ("sub-branch", subbranch)
            elif arg[:2] == "-c":
                cherry = arg[2:]
                print ("cherry-pick", cherry)
            elif arg[:2] == "-d":
                doDel = True
            else:
                prn += " " + arg


if prn == "" and not doDel:
    prn = input ("Enter PRN: ")

prn = prn.strip()

if prn != "":
    if prn[0:3] != "BW-":
        prn = "BW-" + prn

if not " " in prn and not "\t" in prn and not "_" in prn and not doDel : #Already contains description so don't ask for it
    while desc == "" or desc[-12:] == "edit summary":
        desc = input ("Enter Description: ").strip()
else:
    pos1 = prn.find(" ")
    pos2 = prn.find("\t")
    pos3 = prn.find("_")
    pos = len(prn)

    if pos1 > 0 and pos1 < pos:
        pos = pos1

    if pos2 > 0 and pos2 < pos:
        pos = pos2

    if pos3 > 0 and pos3 < pos:
        pos = pos3

    desc = prn[pos+1:].strip()
    prn = prn[0:pos].strip()

desc = desc.replace("_", " ")

cleandesc = re.sub('[^0-9a-zA-Z]+', '_', desc)

if prn != "":
    branch = f"{prn}_{cleandesc}"
else:
    branch = cleandesc

if (branch in branches or "* " + branch in branches):
    branchExists = True

print(f"subbranch = {subbranch}" )

if doDel:
    if subbranch != "":
        delBranch = subbranch
    else:
        delBranch = basebranch

    print(f"git checkout {delBranch}")
    for branch in branches:
        if len(branch) > 0 and branch.strip('* ') != delBranch and branch.strip('* ') != "main" and branch.strip('* ') != subbranch and not "feature/" in branch:
            print (f"git branch -D {branch.strip('* ')}")
    exit(0)

if subbranch != "":
    original_stdout = sys.stdout # Save a reference to the original standard output

    with open(fname, 'w') as f:
        sys.stdout = f
        print("\n***********************************")
        print(f"BRANCH:  {branch}\nMESSAGE: {prn} {desc}\nURL:     https://github.com/cr2product/{basepath}/compare/{subbranch}...{branch}")
        print("*************Commands**************\n")

        print(f"git checkout {subbranch}")
        print("git pull")
        if not branchExists:
            print(f"git checkout -b {branch} {subbranch}")
            print(f"git push -u origin {branch}")
        else:
            print(f"git checkout {branch}")
        print("git pull")
        print(f"git merge {subbranch}")

        if cherry != "":
            print("git fetch c:\\devroot\\mainline\\bw-main")
            print(f"git cherry-pick {cherry}")
        else:
            print("\n*** add and/or commit files in Tortoise GIT ***\n")
            print(f"git checkout {subbranch}")
            print("git pull")
            print(f"git checkout {branch}")
            print(f"git merge {subbranch}")

        print("git push\n")
        sys.stdout = original_stdout
        f.close()

    with open(fname, 'r') as f:
        print(f.read())
        f.close()  

    exit()

if "* " + branch in branches:
    branchCurrent = True
    branchExists = True

commands1 = f"git checkout {basebranch}\ngit pull"
if (not branchExists):
    commands1 += f"\ngit branch {branch}"
commands1 += f"\ngit checkout {branch}\ngit merge {basebranch}"
if (not branchExists):
    commands1 += f"\ngit push -u origin {branch}"

commands2 = "echo ****Add and commit in Tortoise****\npause"
commands3 = f"git checkout {basebranch}\ngit pull\ngit checkout {branch}\ngit merge {basebranch}\ngit push"

original_stdout = sys.stdout # Save a reference to the original standard output

with open(fname, 'w') as f:
    sys.stdout = f

    print("\n***********************************")
    print(f"BRANCH:  {branch}\nMESSAGE: {prn} {desc}\nURL:     https://github.com/cr2product/{basepath}/tree/{branch}")
    print("*************Commands**************\n")
    print(commands1)
    if cherry != "":
        print("git fetch c:\\devroot\\mainline\\bw-main")
        print(f"git cherry-pick {cherry}\ngit push")
    else:
        print("\n****Add and commit in Tortoise****\n")
        print(commands3)

    print("\n***********************************")
    print(f"****Go to github****")
    print(f"https://github.com/cr2product/{basepath}/tree/{branch}")
    print(f"****Click a button \"Compare & pull request\". On the right panel click \"Reviewers\", assign someone to code review, and click button \"Create pull request\".")
    print("\n***********************************")
    print(f"****After code review:")
    print(f"****go to github squash and merge")
    print(f"****delete remote branch on github")

    sys.stdout = original_stdout
    f.close()

with open(fname, 'r') as f:
    print(f.read())
    f.close()



