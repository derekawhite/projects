import re
import os

prn = input ("Enter PRN: ").strip()
desc = ""

if prn[0:3] != "BW-":
    prn = "BW-" + prn

if not " " in prn and not "\t" in prn : #Already contains description so don't as for it
    desc = input ("Enter Description: ").strip()
else:
    pos = prn.find(" ")
    if prn.find("\t") > 0:
        pos = min (pos, prn.find("\t"))
    desc = prn[pos:].strip()
    prn = prn[0:pos].strip()

cleandesc = re.sub('[^0-9a-zA-Z]+', '_', desc)
splitpath = os.getcwd().split('\\')
basepath = "bw-main"
if len(splitpath) >= 4 and splitpath[1] == "devroot":
    basepath = splitpath[3]
branch = f"{prn}_{cleandesc}"

print("\n***********************************")
print(f"BRANCH:  {branch}\nMESSAGE: {prn} {desc}\nURL:     https://github.com/cr2product/{basepath}/tree/{branch}")
print("*************Commands**************\n")
print(f"git checkout {basepath}")
print(f"git checkout -b {branch}")
print(f"git push -u origin {branch}")
print("****Add and commit in Tortoise****")
print(f"git checkout {basepath}")
print(f"git pull")
print(f"git checkout {branch}")
print(f"git merge {basepath}")
print(f"git push")
print("\n***********************************")
print(f"****Go to github****")
print(f"https://github.com/cr2product/{basepath}/tree/{branch}")
print(f"****Click a button \"Compare & pull request\". On the right panel click \"Reviewers\", assign someone to code review, and click button \"Create pull request\".")
print("\n***********************************")
print(f"****After code review:")
print(f"****go to github squash and merge")
print(f"****delete remote branch on github")
print("***********************************")




