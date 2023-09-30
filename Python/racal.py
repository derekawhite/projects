from datetime import datetime
import sys
import functools

def sortbymsg(item1, item2):
    if  item1.id == item2.id:
        return 1 if item1.msg > item2.msg else -1 

    return 1 if item1.id > item2.id else -1 


class message:
    def __init__(self, tm, id, msg):
        self.tm = tm
        self.id = id
        self.msg = msg

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = input ("Enter a filename:")

msgs = []

with open(filename, 'r') as f:
    while True:
        line = f.readline()

        if len(line) == 0:
            break

        sp = line.strip().split(" ")
        try:
            msg = message(datetime.strptime(sp[0], '%H:%M:%S.%f'), sp[1], sp[2])
            msgs.append(msg)
        except:
            pass

msgs.sort(key=functools.cmp_to_key(sortbymsg))

i = 0

print("reg,rsp,id,time")

while i < len(msgs) - 1:
    if msgs[i].id == msgs[i+1].id and ord(msgs[i].msg[1]) == ord(msgs[i+1].msg[1]) - 1:
        diff = (msgs[i+1].tm - msgs[i].tm).total_seconds()
        print (f"{msgs[i].msg},{msgs[i+1].msg},{msgs[i].id},{diff}")
        i = i + 1
    i = i + 1
