import tkinter as tk
from datetime import datetime
from datetime import date, timedelta
import os
import sys

def getClipboardText():
    root = tk.Tk()
    # keep the window from showing
    root.withdraw()
    return root.clipboard_get()

st = getClipboardText()

try:
    file = st.replace("//","/").replace("//","/").replace("%20"," ").replace("file:/","").replace("/","\\").replace("\"", "")

    if os.path.isfile(file):
        print (f"file: \"{file}\"")
        dir = os.path.dirname(file)
    elif os.path.isdir(file):
        dir = file
    else:
        print (f"{file} Not Found")
        exit(1)

    base = os.path.basename(dir);

    if os.path.isdir(dir) and os.path.basename(dir) == "htm":
        dir = os.path.dirname(dir)

    print (f"path: \"{dir}\"")

    if os.path.isdir(dir):
        with open("c:\\devroot\\bin\\cdx.bat", "w") as f:
            f.write(f"cd /d \"{dir}\"\n")
            if "-e" in sys.argv:
                f.write(f"explorer /select,\"{file}\"\n")
            f.close()
    exit(0)
except Exception as e:
    print (f"Error {e}. {st} Not Found")
    exit(1)


