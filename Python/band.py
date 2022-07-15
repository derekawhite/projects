import time
import math
from datetime import datetime

startlength = 10
step = 1
stretch = 20
distance = 0
length = startlength
index = 0
prevpercent = 0

startt = datetime.now()

while True:
    index += 1
    oldlength = length
    length += stretch
    increase = length / oldlength
    distance = (distance + step) * increase
    percent = distance/length * 100

    if distance  > length:
        break;
    if ( index % 100000 == 0):
        diff = datetime.now() - startt
        print ( f"{percent:.2f}% {index:,} {distance:,.2f} {length:,.2f}  Time {diff}")
 

endt = datetime.now()
diff = endt - startt
print ( f"{index:,} {distance:.2f} {length - distance:.2f} {length:.2f} {percent:.2f}%")
print  (f"Steps {index:,} Time {diff}")


