import random
import time

start = 1
end  = 52
cards = 52
orighand = [[],[]]
maxhand = [[],[]]
minhand = [[],[]]

Suits = ["\u2663", "\u2665", "\u2666", "\u2660"] 
Ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'] 

def cardstr (card):
    return f"{Ranks[(card-1)%13]}{Suits[int((card-1)/13)]}"

def Plays(card):
    return 1 if (card - 1)%13 < 10 else (card - 1)%13 - 8

def Court(card):
    return (card - 1)%13 >= 9

def printhand(hand): 
    str = ""
    for i in range(0, len(hand)):
        str += cardstr(hand[i]) + " "
    return str

def printhands(hands): 
    return f"{printhand(hands[0])} {printhand(hands[1])}"

def playhand():
    global orighand
    deck = random.sample(range(start, end +1 ), cards)
    hand = [deck[0:26],deck[26:53]]
    orighand = [hand[0].copy(), hand[1].copy()]

    pile = []
    turn = 0;
    it = 0
    #print(f"hand0: {printhand(hand[0])} hand1: {printhand(hand[1])} pile: {printhand(pile)}")
    while (len(hand[turn]) > 0):
        it += 1
        #print(f"\nIteration: {it}")
        plays = 1
        court = False

        if len(pile) > 0:
            plays = Plays(pile[-1])
            court = Court(pile[-1])
        if (not court):
            pile.append(hand[turn].pop(-1))
        else:
            for i in range (0, plays):
                if len(hand[turn]) < 1:
                    break
                pile.append(hand[turn].pop(-1))
                if (Court(pile[-1])):
                    break;
            if ( not(Court(pile[-1]))):
                #print(f"hand0: {printhand(hand[0])} hand1: {printhand(hand[1])} pile: {printhand(pile)}")
                hand[1-turn] = pile + hand[1-turn]
                pile=[]

        #print(f"hand0: {printhand(hand[0])} hand1: {printhand(hand[1])} pile: {printhand(pile)}")
        turn = 1 - turn    
        if ( it > 10000):
            print( "Inifinte")
            break;

    return it

startt = time.time()

total = 0
max = 0
min = 0

for c in range (1,100000):
    t = playhand()

    if min == 0 or t < min:
        min = t
        minhand = [orighand[0].copy(), orighand[1].copy()]
    if t > max:
        max = t
        maxhand = [orighand[0].copy(), orighand[1].copy()]
    total += t;
    if ( c % 1000 == 0):
        print(f"Count: {c} Mean: {total/c:,.2f}\nMaxhand ({max}): {printhands(maxhand)}\nMinhand ({min}): {printhands(minhand)}\n")

playhand()


















