import sys

if len(sys.argv) < 1:
    print("tobin filename")
    exit(0)

orig_stdout = sys.stdout
out = open(sys.argv[1] + '.txt', 'w')
sys.stdout = out

f = open(sys.argv[1], "rb")
x = f.read()
str = ""
for i in range (0,len(x)):
    h = hex(x[i]).upper()[2:]
    p = hex(i).upper()[2:]
    if (x[i] >= 0x20 and x[i] < 0x80 ):
        str += chr(x[i])
    else:
        str += "."
    if ( i%16 == 0):
        print(f"{p.rjust(10,' ')}: ", end='')
    print(f"{h.rjust(2,'0')} ", end='')
    if (i%8==7):
        print(" ", end='')
    if (i%16==15):
        print(f" {str}")
        str = ""

print(f"{str.rjust(51-len(str)*2 ,' ')}")
      
f.close()
sys.stdout = orig_stdout
out.close()

print(f"\n\n{sys.argv[1]}.txt\n")

