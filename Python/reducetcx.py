from lxml import etree
import os
import sys

nMaxPoints = 0
if (len(sys.argv) < 2):
    print("Usage: reducetcx [input file] <trackpoints>\n")
    exit()
else:
    stXMLFile = sys.argv[1]

if (len(sys.argv) > 2 and sys.argv[2].isnumeric):
    nMaxPoints = (int)(sys.argv[2])

stOutFile = os.path.splitext(stXMLFile)[0]+ "out"+ os.path.splitext(stXMLFile)[1]
root = etree.parse(stXMLFile)

for elem in root.getiterator():
    if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
        elem.tag = etree.QName(elem).localname

for node in root.findall('.//Trackpoint'):
    if node.find(".//Position") == None:
        node.getparent().remove(node)

if nMaxPoints != 0:
    nDivisor = (int)(len(root.findall('.//Trackpoint')) / nMaxPoints)
    nPoint = 0
    for node in root.findall('.//Trackpoint'):
        nPoint += 1
        if nPoint % nDivisor != 0:
            node.getparent().remove(node)

with open(stOutFile, 'w') as f:
    print ("Output file is", stOutFile)
    f.write(etree.tostring(root).decode())
    f.close()
