import re
import os
import sys
import subprocess

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

if (len(sys.argv) > 1):
    for index, arg in enumerate(sys.argv):
        if index > 0:
            prn += " " + arg
else:
    prn = input ("Enter PRN: ")

prn = prn.strip()

if prn != "":
    if prn[0:3] != "BW-":
        prn = "BW-" + prn

if not " " in prn and not "\t" in prn and not "_" in prn : #Already contains description so don't ask for it
    while desc == "":
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
splitpath = os.getcwd().split('\\')
basepath = "bw-main"
basebranch = "main"
if len(splitpath) >= 4 and splitpath[1] == "devroot":
    basepath = splitpath[3]
if prn != "":
    branch = f"{prn}_{cleandesc}"
else:
    branch = cleandesc

if basepath == "bw-main":
    basebranch = "main"
else:
    basebranch = basepath

if (branch in branches):
    branchExists = True

if ("* " + branch in branches):
    branchCurrent = True
    branchExists = True

commands1 = f"git checkout {basebranch}\r\ngit pull"
if (not branchExists):
    commands1 += f"\r\ngit branch {branch}"
commands1 += f"\r\ngit checkout {branch}\r\ngit merge {basebranch}"
if (not branchExists):
    commands1 += f"\r\ngit push -u origin {branch}"

commands2 = "echo ****Add and commit in Tortoise****\r\npause"
commands3 = f"git checkout {basebranch}\r\ngit pull\r\ngit checkout {branch}\r\ngit merge {basebranch}\r\ngit push"


print("\n***********************************")
print(f"BRANCH:  {branch}\nMESSAGE: {prn} {desc}\nURL:     https://github.com/cr2product/{basepath}/tree/{branch}")
print("*************Commands**************\n")
print(commands1)
print("\r\n****Add and commit in Tortoise****\r\n")
print(commands3)
print("\n***********************************")
print(f"****Go to github****")
print(f"https://github.com/cr2product/{basepath}/tree/{branch}")
print(f"****Click a button \"Compare & pull request\". On the right panel click \"Reviewers\", assign someone to code review, and click button \"Create pull request\".")
print("\n***********************************")
print(f"****After code review:")
print(f"****go to github squash and merge")
print(f"****delete remote branch on github")


