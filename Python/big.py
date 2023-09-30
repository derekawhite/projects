import time

r = 0
g = int(pow(10,100)) #Googol

def sleepy(n,l):
    print (f"Sleeping for {n}*{l} seconds")
    for i in range(0, n):
        time.sleep(l)

def sleep1year():
    print (f"Sleeping for 1 year")
    sleepy(365, 24*60*60)

def sleep1second():
    print (f"Sleeping for 1 second")
    time.sleep(1)

def recurse(b, p, func):
    global r,n
    r += 1
    for a in range (0,b):
        if r < p:            
            recurse(b,p,func)
        else:
            func()
    r -= 1

base = int(eval(input("Enter base: ")))
power = int(eval(input("Enter power: ")))
tm = input("Enter s (seconds) or y (years): ")

for a in range ( 0, g):
 for b in range ( 0, g):
  for c in range ( 0, g):
   for d in range ( 0, g):
    for e in range ( 0, g):
     for f in range ( 0, g):
      for g in range ( 0, g):        
       for h in range ( 0, g):
        for i in range ( 0, g):
         for j in range ( 0, g):
          for k in range ( 0, g):
           for l in range ( 0, g):
            for m in range ( 0, g):
             for n in range ( 0, g):          
              for o in range ( 0, g):  
               for p in range ( 0, g):  
                for q in range ( 0, g):  
                 for r in range ( 0, g):  
                  for s in range ( 0, g):  
                   for t in range ( 0, g):  # an extra 2000 0s
                            r = 0
                            print (f"About to sleep for {base}^{power} * 10^2000 {'years' if tm == 'y' else 'seconds'}")
                            recurse(base, power, sleep1year if tm == 'y' else sleep1second)
