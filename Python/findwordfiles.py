import fnmatch
import os
import docx2txt
import sys
from win32com import client as wc

def scandir(pattern):
    files = []
    for root, dirnames, filenames in os.walk('.'):
        for filename in fnmatch.filter(filenames, pattern):
            path = os.path.realpath(os.path.join(root, filename))
            files.append(path)  
    return files  

months = ['January', 'February', 'March', 'April', 'May', 'June',' July', 'August', 'September', 'October', 'November', 'December']
if len(sys.argv) > 1:
    findstr = sys.argv[1:]
else:
    findstr = input ("Enter a string(s) to find:").split()

print (sys.argv)
print (findstr)

w = wc.Dispatch('Word.Application')
docfiles = scandir("*.doc")
for  file in docfiles:
    if not os.path.isfile(file+'x'):
        print (f"saving {file} as {file+'x'}")
        try:
            doc=w.Documents.Open(os.path.abspath(file))
            doc.SaveAs(file+"x",16)
            doc.Close();
        except:
            print (f"error saving {file} as {file+'x'}")            

docxfiles = scandir("*.docx")
os.system('cls')
nFound = 0

for  file in docxfiles:
    try:
        my_text = docx2txt.process(file)
    except:
        print (f"error reading {file}")            
        continue

    lastdate = ""        
    lines=my_text.split('\n')
    for line in lines:
        if any (m in line for m in months):
            lastdate = line
        found = len(findstr) > 0
        for str in findstr:
            if  len(str) > 0 and str[0] == "+":
                found = str[1:].upper() in line.upper()
            else:     
                words = line.upper().split()
                for i in range (len(words)):
                    words[i] = ''.join(ch for ch in words[i] if ch.isalnum())

                if not str.upper() in words:
                    found = False;
        if found:
            nFound += 1
            print(f"File: {file}\nDate: {lastdate}\nLine: {line}\n\n")
print(f"{nFound} found in {len(docxfiles)} files")