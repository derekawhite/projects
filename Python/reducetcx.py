import math
from lxml import etree
import os
import sys


nMaxPoints = 300
nMinAngle = 10
nOffset = 0
stXMLFile = None

def calcangle(x1, y1, x2, y2):
    ret = 0
    if x1 == x2:
        if y2 > y1:
            ret = 90
        else:
            ret = -90
    else:
        if  x2 < x1:
            ret = 180 + math.atan((y2 - y1)/(x2 - x1)) / math.pi * 180
        else:
            ret = math.atan((y2 - y1)/(x2 - x1)) / math.pi * 180

    if  ret < -180:
        ret += 360
    if ret > 180:
        ret -= 360

    return ret

def getanglediff (node1, node2, node3):
    if node1 == None or node2 == None or node3 == None:
        return 0

    try:
        x1 = float(node1.find("Position//LatitudeDegrees").text)
        y1 = float(node1.find("Position//LongitudeDegrees").text)
        x2 = float(node2.find("Position//LatitudeDegrees").text)
        y2 = float(node2.find("Position//LongitudeDegrees").text)
        x3 = float(node3.find("Position//LatitudeDegrees").text)
        y3 = float(node3.find("Position//LongitudeDegrees").text)

        a1 = calcangle (x1, y1, x2, y2)
        a2 = calcangle (x2, y2, x3, y3)
        return abs(a1 - a2)

    except:
        return 90

print("Usage: reducetcx [input file] <trackpoints>\n")

if len(sys.argv) <=1:
    print ("reducetcx file maxpoints maxangle")
    exit(0)

if len(sys.argv) > 1:
    stXMLFile = sys.argv[1]

if (len(sys.argv) > 2 and sys.argv[2].isnumeric):
    nMaxPoints = (int)(sys.argv[2])
if (len(sys.argv) > 3 and sys.argv[3].isnumeric):
    nMinAngle = (int)(sys.argv[3])

if stXMLFile == None:
    nMinAngle = 10
    nMaxPoints = 500
    stXMLFile = "C:\\Users\\Derek\\Downloads\\Belgard.tcx"    

stOutFile = os.path.splitext(stXMLFile)[0]+ "out"+ os.path.splitext(stXMLFile)[1]
root = etree.parse(stXMLFile)

for elem in root.getiterator():
    if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
        elem.tag = etree.QName(elem).localname

nodes = root.findall('.//Trackpoint') 
print (f"Original number of points: {len(nodes)}")
for node in nodes:
    if node.find(".//Position") == None:
        node.getparent().remove(node)

nodes = root.findall('.//Trackpoint')    
print (f"Fixed    number of points: {len(nodes)}")

if nMaxPoints > 0:
    nDivisor = (int)(len(root.findall('.//Trackpoint')) / nMaxPoints)
    for nPoint in range(0, len(nodes) - 1, 1):
            nIndex = nPoint - nOffset
            if nDivisor != 0 and nPoint % nDivisor != 0:
                nodes[nIndex].getparent().remove(nodes[nIndex -1])      
                nodes.remove(nodes[nIndex -1])
                nOffset += 1 

print (f"Reduced  number of points: {len(nodes)}")

nOffset = 0
if nMinAngle > 0:
    for nPoint in range(2, len(nodes) - 1, 1):
        nIndex = nPoint - nOffset
        if nIndex < len(nodes):
            angle = getanglediff(nodes[nIndex - 2], nodes[nIndex -1], nodes[nIndex])
            if angle < nMinAngle:
                nodes[nIndex].getparent().remove(nodes[nIndex -1])      
                nodes.remove(nodes[nIndex -1])
                nOffset += 1 
      
with open(stOutFile, 'w') as f:
    print (f"Final    number of points: {len(nodes)}")
    print (f"\nOutput file is {stOutFile}")
    f.write(etree.tostring(root).decode())
    f.close()
