import time
import sys
import textwrap




def logfact(n):
    from math import log
    sum = 0
    for i in range(1, n+1):
        sum = sum + log(i)
    return sum / log(10)

def smallvalapprox(n):
    from math import log, pi
    return ((n+1)*log(n) - n)/ log(10)

def stirling(n):
    from math import log, pi
    return (n*log(n) - n + 0.5*log(n) + 0.5*log(2*pi))/log(10)

def stirlinge(n):
    from math import log, pi
    return (n*log(n) - n + 0.5*log(n) + 0.5*log(2*pi) + log(1+(1.0/12*n)))/log(10)

def r(n):
    from math import log, exp, sqrt, pi
    #return sqrt((2*x + (1.0/3))*pi) * (x**pi)*(exp(-x))                                                                                                           
    return (n*log(n) - n + (log(n*(1+4*n*(1+2*n))))/6 + log(pi)/2)/log(10)


def logfactapprox(x):
    print ("*************")
    print ("value to take the log factorial of is", x)
    print ("Exact value is", logfact(x))
    print ("Small value approximation (K.V. Raman) is", smallvalapprox(x))
    print ("Stirling is", stirling(x))
    print ("Stirling with extra term is", stirlinge(x))
    print ("Ramanujan is", r(x))
    print ("*************")

power = 1


def factorial(x):
    tic = time.perf_counter()
    toc = time.perf_counter()
    fact = list([1])
    nSteps = 0
    carry = 0
    power10 = 10**power

    for i in range(2, x+1):
        for j in range(len(fact) - 1, -1, -1):
            nSteps += 1
            prod = fact[j] * i + carry
            carry = prod // power10
            fact[j] = prod % power10

        while carry > 0:
            fact.insert(0, carry % power10)
            carry //= power10

        if (i % 1000 == 0):
            print(f"{i} steps: {nSteps:,}")

    filename = f"{x}_factorial.txt"
    original_stdout = sys.stdout  # Save a reference to the original standard output

    with open(filename, 'w') as f:
        sys.stdout = f  # Change the standard output to the file we created.

        print(f"{x}! = \n", end='')
        index = 0
        factorial = ""

        for n in fact:
            index += 1
            factorial += f"{n:0{power}}"
        factorial = factorial.lstrip("0")
        print('\n'.join(textwrap.wrap(factorial, 80)))
        print(f"\n{x}! Length = {len(factorial):,} Steps: {nSteps:,}")

        toc = time.perf_counter()
        print(f"Completed in {toc - tic:0.4f} seconds")
    sys.stdout = original_stdout

    print(f"Completed in {toc - tic:0.4f} seconds")
    print(f"\n{x}! Length = {len(factorial):,} Steps: {nSteps:,}")
    print(f"Result in {filename}\n")


while True:
    print ("Factorial generation")
    n = 1
    if len(sys.argv) > 1 and sys.argv[1].isnumeric():
        n = (int)( sys.argv[1])
    else:
        n = int(input("Enter a number: "))

    if n == 999:
        break

    if len(sys.argv) > 2 and sys.argv[2].isnumeric():
        power = (int)( sys.argv[2])
    else:
        power = int(input("Enter power of 10: "))

    #logfactapprox(n)

    factorial(n)
    if len(sys.argv) > 1:
        break

