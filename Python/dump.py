instr = False

f = open("c:\\temp\\h_sar_issft-1.dmp", "rb")
fo = open("c:\\temp\\h_sar_issft-1.dmp.asc", "w")

data = f.read()
dataout = ""

for index, by in enumerate(data):
    if data[index] >= 32 and data[index] < 127:
        instr = True
        dataout += (chr(by))
    elif instr:
        instr = False
        dataout += ('\n')

fo.write(dataout)
f.close()
fo.close()
