#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org pyperclip
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org win32gui

import tkinter as tk
from datetime import datetime
from datetime import date, timedelta
import os
import pyperclip

#import win32gui


def getClipboardText():
    root = tk.Tk()
    # keep the window from showing
    root.withdraw()
    return root.clipboard_get()

def setClipboardText(st):
    pyperclip.copy(st)

st = getClipboardText()
lines = st.split('\n')
cl = ''.join(st.split())
setClipboardText(cl)

now = datetime.now()
dt =  now.strftime("%Y%m%d%H%M%S")

for i in range(0, len(lines)):
    line = lines[i]
    if "cannot open file '" in line:
        start = line.find("cannot open file '")   
        end = line.find("'",line.find("'")+1)
        oldfilename = line[start + 18:end];
        newfilename = f"{oldfilename}_!!_{dt}"
        if os.path.isfile(oldfilename):
            print ( f"renaming {oldfilename} to {newfilename}")
            os.rename (oldfilename, newfilename);
    elif "cannot open " in line:
        start = line.find("cannot open ")   
        end = line.find(" ",start+12)
        oldfilename = line[start + 12:end];
        newfilename = f"{oldfilename}_!!_{dt}"
        print (f"{line}\n{oldfilename}\n{newfilename}\n")
        if os.path.isfile(oldfilename):
            print ( f"renaming {oldfilename} to {newfilename}")
            os.rename (oldfilename, newfilename);
