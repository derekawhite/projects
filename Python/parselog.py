import os
import xml.etree.ElementTree as ET
import sys

hex = '1234567890ABCDEFabcdef'
lines = []
binaryoffset = 0
    
class IsoField:
    def __init__(self, startline):
        global binaryoffset
        self.field = ""
        self.len = 0
        self.isotype = 'X'
        self.isonum = 0
        i = startline
        self.nextline = i + 1
        self.data = ""
        while i < len(lines) - 1 and (" Field " not in lines[i] or "] length " not in lines[i]) and self.nextline != -1:
            if "***********************************************************" in lines[i]:
                self.nextline = -1
            else:
                i += 1
                self.nextline = i
                if  (" Field " in lines[i] and "] length " in lines[i]):
                    sp = lines[i].strip().split(' ')
                    iField = sp.index("Field")
                    iLen = sp.index("length")

                    if iField < len(sp) - 1:
                        self.field = sp[iField+1]
                        self.isotype = self.field[0]
                        if self.field[1:].isnumeric:
                            self.isonum = int(self.field[1:])

                    if iLen < len(sp) - 1 and sp[iLen+1].isnumeric():             
                        self.len = int(sp[iLen+1])

                        if binaryoffset == 0 and self.len > 0:
                            data1 = lines[i+1].strip()
                            binaryoffset = len(data1) - min(16, self.len) - 52

                        for j in range (0,  int(self.len/16) + 1):
                            for k in range (0, min(self.len - j * 16, 16)):
                                self.data+=lines[i+j+1][binaryoffset + 3 * k:binaryoffset + 3 * k+2]
                        
                        try:
                            byt = bytes.fromhex(self.data)
                        except:
                            self.data = stringtohexstring ("Hidden")
                            self.len = 6


    def stringdata(self):
        return hexarraytotring(self.data)
     
    def binarydata(self):
        return self.data    
    
    def IsBinary(self):
        byt = bytes.fromhex(self.data)

        for b in byt:
            if b < 32 or b >= 127:
                return True
        return False 

def stringtohexarray(str):
    ret = []
    l = list(str)
    for s in l:
        ret.append("{0:02x}".format(ord(s)))
    return ret
 
def hexarraytotring(str):
    ret = ""
    byt = bytes.fromhex(str)

    for b in byt:
        if b >= 32 and b < 127:
            ret += chr(b)
        else:
            ret += '.'
    return ret

def stringtohexstring(str):
    ret = ""
    l = list(str)
    for s in l:
        ret += ("{0:02x}".format(ord(s)))
    return ret

def findtxn(startline):
    for i in range (startline, len(lines)):
        if "*** Request In From Network Received ***" in lines[i]:
            return i
    return -1
  
def GenerateXML(fileName, mti) :
      
    if os.path.exists(fileName):
        tree = ET.parse(fileName)
        root = tree.getroot()
    else:
        root = ET.Element("Netsim", {'network':'cr2'})     

    m = ET.Element("message", {'name':'Outgoing ' + mti})   
    root.append (m)

    for field in isofields:
        b = ET.SubElement(m, "required", {'field':field.field})
        if field.isonum == 37:
            ET.SubElement(ET.SubElement(b, "increment"), "text").text="RRN"
        elif field.isonum == 11:
            ET.SubElement(ET.SubElement(b, "increment"), "text").text="STAN"      
        elif field.isonum == 7:
            ET.SubElement(b, "timestamp", {'format':'MMDDhhmmss','timezone':'GMT'})
        elif field.isonum == 12:
            ET.SubElement(b, "timestamp", {'format':'hhmmss','timezone':'local'})
        elif field.isonum == 13:
            ET.SubElement(b, "timestamp", {'format':'MMDD','timezone':'local'})
        elif field.IsBinary():
            ET.SubElement(b, "data").text = field.binarydata()
        else:
            ET.SubElement(b, "text").text = field.stringdata()            



    if not root.find("counter[@name='RRN']"):
        m = ET.Element("counter", {'name':'RRN'})   
        root.append (m)
        ET.SubElement(ET.SubElement(m, "current"), "text").text = "1"
        ET.SubElement(ET.SubElement(m, "minimum"), "text").text = "1"
        ET.SubElement(ET.SubElement(m, "maximum"), "text").text = "10000000"

    if not root.find("counter[@name='STAN']"):
        m = ET.Element("counter", {'name':'STAN'})   
        root.append (m)
        ET.SubElement(ET.SubElement(m, "current"), "text").text = "1"
        ET.SubElement(ET.SubElement(m, "minimum"), "text").text = "1"
        ET.SubElement(ET.SubElement(m, "maximum"), "text").text = "999999"

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ", level=0)
    tree.write(fileName, encoding="utf-8", xml_declaration=True)
                      
filename = os.path.abspath(sys.argv[1])
print (f"File {filename}")
f1=open(filename)
lines = f1.readlines()
mti = ""
rrntofind = sys.argv[2]
rrn  =""
txnstart = 0
foundRRN = False
xmlfile = r"c:\temp\test.xml"

while not foundRRN and txnstart < len(lines) and txnstart >= 0:
    txnstart = findtxn (txnstart)
    isofields = []      
    foundmti = False
    while txnstart >= 0 and txnstart < len(lines):
        field = IsoField(txnstart)
        if  field.nextline == -1:
            break
        txnstart = field.nextline

        if field.len > 0:
            if field.isotype == 'C' and field.isonum == 1:
                if foundmti:
                    break
                foundmti = True
                mti = field.stringdata()
            if not((field.isotype == 'C' and field.isonum == 2) or (field.isotype == 'P' and field.isonum == 1)):
                isofields.append(field)
            if field.isotype == 'P' and field.isonum == 37:
                rrn = field.stringdata()
    foundRRN = rrn ==  rrntofind
    txnstart += 1

if foundRRN:
    GenerateXML(xmlfile, mti)
    print (f"Generated xml file {xmlfile} from {filename}")
else:
    print (f"Failed to find rrn {rrntofind}")







