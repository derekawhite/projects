import numpy as np
import math

ones = np.array(["", "one ", "two ", "three ", "four ", "five ", "six ", "seven ", "eight ", "nine ",
                "ten ", "eleven ", "twelve ", "thirteen ", "fourteen ", "fifteen ", "sixteen ", "seventeen ", 
                "eighteen ", "nineteen "])

tens = np.array(["", "", "twenty ", "thirty ", "forty ", "fifty ", "sixty ", "seventy ", "eighty ", "ninety "])

powers = np.array(["", "thousand ", "million ", "billion ", "trillion ", "quadrillion "])

def get_ones(x):
    if  x % 100 < 20:
        return ones[x % 20]
    else:
        return ones[x % 10]

def get_tens(x):
    return tens[(x % 100)//10]

def get_hundreds(x):
    n = (x%1000)//100
    hundreds = get_ones((x%1000)//100)
    if hundreds != "":
        hundreds += "hundred "  
        if x % 100 != 0:      
            hundreds += "and "
    return hundreds


def get_power(x, power):
    pow10 = round(math.pow(10, power))
    n = round((x%(pow10*1000))//pow10)
    thousands = f"{get_hundreds(n)}{get_tens(n)}{get_ones(n)}"  
    if thousands != "":
        thousands += powers[power//3]
        if x % pow10 < pow10//10 and x % pow10 != 0:      
            thousands += "and "
        else:
            thousands = thousands.strip() + ", "
   
    return thousands

while True:
    n = int(input ("Enter a number:"))
    print ( f"{n:,}\n{get_power(n, 15)}{get_power(n, 12)}{get_power(n, 9)}{get_power(n, 6)}{get_power(n, 3)}{get_hundreds(n)}{get_tens(n)}{get_ones(n)}")
    if n == 999:
        break;
