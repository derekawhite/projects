import psutil
import os
import sys

def kill(process_names):
    for process in psutil.process_iter():
        try:
            for name in process_names:
                if name in process.name() or ("\\" in name and name in process.exe()):
                    print(f'Stopping {process.exe()}')
                    process.terminate()
        except Exception:
            None

exes = []
if "-j" in sys.argv:
    exes.append ("java.exe")
if "-b" in sys.argv or len(sys.argv) <= 1:
    print ("Stopping BankWorld Controller...")
    os.system("net stop \"BankWorld Controller\"")
    exes.append ("BWOut\\Debug")

for index, arg in enumerate(sys.argv):
    if index > 0 and arg != "-j" and arg != "-b":
        exes.append(arg)
kill (exes)
    
