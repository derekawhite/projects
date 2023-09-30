import os
import sys
import random
import functools

find = exclude = include = notthere = ""
printlen = 5
guesses = []
results = []
uncommon = False
loop = True
endlen = 5

class substr:
    def __init__(self, str):
        self.str = str
        self.count = 1

def sortbyendinglen(subs1, subs2):

    if len(subs1.str) != len(subs2.str):
        return 1 if len(subs1.str) > len(subs2.str) else -1  

    if subs1.count != subs2.count:
        return 1 if subs1.count < subs2.count else -1         

    return 1 if subs1.str > subs2.str else -1  

def DoEndings(words):
    endings = set ()
    substrs = set ()

    for wlen in range (1, 7):
        print ("wlen", wlen)
        for word in words:
            if len(word) > wlen:
                ending = word[len(word) - wlen:]
                
                if not ending in endings:
                    endings.add (ending)
                    substrs.add(substr(ending))
                else:
                    matches = [x for x in substrs if x.str == ending]
                    if len(matches) == 1:
                        matches[0].count += 1
                   
    result = list(substrs)
    result.sort(key=functools.cmp_to_key(sortbyendinglen))

    for subs in result:
        print (f"Ending {subs.str.rjust(8)} Count {subs.count}")

def load_words(filename):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)) as word_file:
        valid_words = set(word_file.read().split())
    return valid_words

def find_words(words, find):
    matches = []
    for word in words:
        if match(word, find):
            matches.append (word)

    matches.sort()
    return matches

def sortbyending(word1, word2):
    global endlen
    end1 = word1[max(0, len(word1) - endlen):]
    end2 = word2[max(0, len(word2) - endlen):]

    if  end1 != end2:
        return 1 if end1 > end2 else -1 

    return 1 if word1 > word2 else -1 

def reversesort(word1, word2):
    return 1 if word1[::-1] > word2[::-1] else -1    

def DoRightJustify(words, find):
    if find != "":
        matches = find_words(words, find)
    else:
        matches = list(words)

    matches.sort(key=functools.cmp_to_key(reversesort))
    for word in matches:
        print(word.rjust(32))
        
def DoAlphabetical(words):

    matches=  []
    for word in words:
        x = list (word)
        x.sort()
        if x == list (word):
           matches.append (word)  
    matches.sort()
    for word in matches:
        print (word)

    

def DoCommonEnding(words):
    lenwords = list(w for w in words if len(w) > endlen)
    lenwords.sort(key=functools.cmp_to_key(sortbyending))
    run = 1
    maxrun = 1
    maxrunindex = 1   
    maxrunending = "" 


    for i, w in enumerate(lenwords):
        if i < len(lenwords) - 1 and lenwords[i][len(lenwords[i]) - endlen:] == lenwords[i+1][len(lenwords[i+1]) - endlen:]:
            run+=1;
        else:
            run = 1

        if run > maxrun:
            maxrun = run
            maxrunending = lenwords[i][len(lenwords[i]) - endlen:]
            maxrunindex = i - run + 2


    for i in range (maxrunindex, maxrunindex + maxrun):
        print (lenwords[i])

    print (f"Max run of ending {maxrunending} of length {endlen} = {maxrun} at index {maxrunindex}")


def DoWordle():
    global exclude
    global find
    global notthere
    global include

    line = input("Enter guess and result. Enter to finish: ").split()
    if (len(line) == 2 and len(line[0]) == len(line[1])):
        guess = line[0]
        result = line[1]        
        for i in range (0, len(guess)):
            if result[i] == 'g': 
                find = find[:i] + guess[i] + find[i+1:]
                include += guess[i]
            elif result[i] == 'o': 
                notthere = notthere[:i] + guess[i] + notthere[i+1:]
                include += guess[i]

        for i in range (0, len(guess)):
            if result[i] != 'g' and result[i] != 'o' and not guess[i] in include:
                exclude += guess[i]
    elif len(line) == 0:
        exit()
    else:
        print("Invalid input")

def DoPattern(words, length):
    pattern = ""
    for w in words:
        if len(w) == length and len(find_words(words, w.upper())) == 1:
            print (w)
               
def match (word, find):
    l = len(word)
    if (l != len(find)):
        return False
    
    for i in range(0, l):
        if find[i] != "_" and find[i] != '-':
            if find[i] >= 'a' and find[i] <= 'z' and find[i] != word[i]:
                return False 
            if find[i] < 'a' or find[i] > 'z':
                for j in range(i+1, l):
                    if (find[j] == find[i] and word[j] != word[i]) or (find[j] != find[i] and word[j] == word[i]):
                        return False 

    for w in list(include):
        if not w in word:
            return False

    for w in list(exclude):
        if w in word:
            return False

    for i in range (0, len(notthere)):
        if word[i] == notthere[i]:
            return False      

    for i in range(0, len(results)):
        for j in range (0, len(results[i])):
            if word[j] != find[j]:
                return False      


    return True

all_words = load_words('words_alpha.txt')
common_words = load_words('common_words.txt')

if len(sys.argv) > 1:
    for i in range (1, len(sys.argv)):
        if sys.argv[i].isnumeric():
            find += chr(int(sys.argv[i]) + ord('A') - 1)
            loop = False
        elif sys.argv[i][0] == "!":
            exclude = sys.argv[i][1:]
        elif sys.argv[i][0] == "~":
            include = sys.argv[i][1:]
        elif sys.argv[i][0] == "$":
            notthere = sys.argv[i][1:]
        elif sys.argv[i][0:2] == "-l" and sys.argv[i][2:].isnumeric():
            printlen = int(sys.argv[i][2:])
        elif sys.argv[i][0:2] == "-u":
            uncommon = True
        elif sys.argv[i][0:2] == "-c" and sys.argv[i][2:].isnumeric():
            endlen = int(sys.argv[i][2:])
            DoCommonEnding(common_words)
            exit()
        elif sys.argv[i] == "-rj":
            DoRightJustify(common_words, "")
            exit()
        elif sys.argv[i] == "-ao":
            DoAlphabetical(common_words)
            exit()
        elif sys.argv[i] == "-e":
            DoEndings(common_words)
            exit()            
        elif sys.argv[i][0:2] == "-p" and sys.argv[i][2:].isnumeric():
            DoPattern(common_words, int(sys.argv[i][2:]))
            exit()     
        else:
            find += sys.argv[i]
            loop = False
if loop:
    find = input("Enter template: ")

if notthere == "":
    notthere = "".ljust(len(find) ,'-')

while True:
    print("Find = ", find)
    matches = find_words(common_words, find)
 
    print (len(matches), "common words found")  
    for i in range (0, min(printlen, len(matches))):
        print (matches[i])

    if uncommon:
        amatches = find_words(all_words, find)
        umatches = []
        for i in range (0,len(amatches)):
            if not amatches[i] in matches:
                umatches.append(amatches[i])

        print (len(umatches), "other words found")    
        for i in range (0, min(printlen, len(umatches))):
            print (umatches[i])

    if not loop:
        exit()
    
    DoWordle()
    print (find, exclude, include, notthere)        

