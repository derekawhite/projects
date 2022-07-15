import numpy as np
from turtle import Turtle, Screen
import time
from datetime import datetime

from time import sleep
from turtle import Screen, Turtle
from pynput.mouse import Listener


gridsize = 80
iterations = 1000000
scale = 10
paused = False
mutate = True
turtle = Turtle(visible=False)
screen = Screen()
grid = np.zeros(gridsize*gridsize).reshape(gridsize, gridsize)

def addGosperGliderGun(i, j):
    global mutate
    mutate = False
    gun = np.zeros(11*38).reshape(11, 38)

    gun[5][1] = gun[5][2] = 1
    gun[6][1] = gun[6][2] = 1

    gun[3][13] = gun[3][14] = 1
    gun[4][12] = gun[4][16] = 1
    gun[5][11] = gun[5][17] = 1
    gun[6][11] = gun[6][15] = gun[6][17] = gun[6][18] = 1
    gun[7][11] = gun[7][17] = 1
    gun[8][12] = gun[8][16] = 1
    gun[9][13] = gun[9][14] = 1

    gun[1][25] = 1
    gun[2][23] = gun[2][25] = 1
    gun[3][21] = gun[3][22] = 1
    gun[4][21] = gun[4][22] = 1
    gun[5][21] = gun[5][22] = 1
    gun[6][23] = gun[6][25] = 1
    gun[7][25] = 1

    gun[3][35] = gun[3][36] = 1
    gun[4][35] = gun[4][36] = 1

    grid[i:i+11, j:j+38] = gun


def add2(i, j):
    global mutate
    mutate = False
    gun = np.zeros(10*3).reshape(10, 3)
    gun[0][1] = gun[1][1] = 1
    gun[2][0] = gun[2][2] = 1
    gun[3][1] = gun[4][1] = gun[5][1]= gun[6][1] = 1
    gun[7][0] = gun[7][2] = 1
    gun[8][1] = gun[9][1] = 1

    grid[i:i+10, j:j+3] = gun

def add3(i, j):
    global mutate
    mutate = False
    gun = np.zeros(1*39).reshape(1, 39)
    gun[0][0] = gun[0][1] = gun[0][2] = gun[0][3] = gun[0][4] = gun[0][5] = gun[0][6] = gun[0][7] = 1
    gun[0][9] = gun[0][10] = gun[0][11] = gun[0][12] = gun[0][13] = 1
    gun[0][17] = gun[0][18] = gun[0][19] = 1
    gun[0][26] = gun[0][27] = gun[0][28] = gun[0][29] = gun[0][30] = gun[0][31] = gun[0][32] = gun[0][7] = 1
    gun[0][34] = gun[0][35] = gun[0][36] = gun[0][37] = gun[0][38] = 1

    grid[i:i+1, j:j+39] = gun

def drawborder(turtle):
    turtle.penup()
    turtle.setposition((-gridsize/2) * scale - scale, (-gridsize/2) * scale - scale)
    turtle.setheading(0)
    turtle.pendown()
    turtle.forward(gridsize*scale+scale)
    turtle.left(90)
    turtle.forward(gridsize*scale+scale)
    turtle.left(90)
    turtle.forward(gridsize*scale+scale)
    turtle.left(90)
    turtle.forward(gridsize*scale+scale)
    turtle.penup()

def drag(i,j): 
   print (i,j)

def clickfun3(i,j): 
    global paused
    paused = False

def clickfun1(i,j): 
    global paused
    paused = True
    row = round(i/scale + gridsize/2)
    col = round(j/scale + gridsize/2)

    grid[row][col] = 1 - grid[row][col]

    turtle.setposition((row - gridsize/2) * scale, (col - gridsize/2) * scale) 
    if ( grid[row][col] == 1):
        turtle.dot(scale, 'black')
    else:
        turtle.dot(scale, 'white')

def keyc():
    grid.fill(0)

def key1():
    grid.fill(0)
    addGosperGliderGun (20,20)

def key2():
    grid.fill(0)
    add2 (20,20)

def key3():
    grid.fill(0)
    add3 (40,40)

def gameoflife():
    global mutate
    global grid

    screen.setup(gridsize * (scale) + 30, gridsize * (scale) + 30)
    screen.title("Game of life")

    screen.onscreenclick(clickfun1, 1)
    screen.onscreenclick(clickfun3, 3)
    screen.onkeypress(key1, "1")
    screen.onkeypress(key2, "2")
    screen.onkeypress(key3, "3")
    screen.onkeypress(keyc, "c")
    screen.listen()

    turtle.speed(0)
    turtle.ht()

    gun = np.zeros(11*11).reshape(11, 11)
    gun[0][1] = 1
    gun[1][2] = 1
    gun[2][0] = gun[2][1] = gun[2][2] = 1
    gun[8][6] = 1
    gun[7][7] = 1
    gun[6][5] = gun[6][6] = gun[6][7] = 1
    gun[10][8] = gun[10][9] = gun[10][10] = 1
  
    grid[22:33, 22:33] = gun

    for iter in range(iterations):

        while paused:
            screen.update()
            sleep(0.1)

        drawborder(turtle)
        newgrid = grid.copy()
        screen.tracer(False)

        for row in range(gridsize):
            for col in range(gridsize):
                prevrow = row - 1 if row > 0 else gridsize - 1
                prevcol = col - 1 if col > 0 else gridsize - 1
                nextrow = row + 1 if row < gridsize - 1 else 0
                nextcol = col + 1 if col < gridsize - 1 else 0

                livecells = newgrid[prevrow][prevcol] + newgrid[prevrow][col] + newgrid[prevrow][nextcol] + \
                            newgrid[row][prevcol] + newgrid[row][nextcol] + \
                            newgrid[nextrow][prevcol] + newgrid[nextrow][col] + newgrid[nextrow][nextcol]

                if mutate:
                    if livecells == 3:
                        grid[row][col] = 1
                    elif livecells == 2:             
                        grid[row][col] = newgrid[row][col]
                    else:
                        grid[row][col] = 0

                if grid[row][col] != newgrid[row][col] or grid[row][col] == 1:
                    turtle.setposition((row - gridsize/2) * scale, (col - gridsize/2) * scale)                    
                    if ( grid[row][col] == 1):
                        turtle.dot(scale, 'black')
                    else:
                        turtle.dot(scale, 'white')

        mutate = True
        screen.title(f"Game of life generation {iter}")
        screen.update()
        if not paused:
            turtle.clear() 
        time.sleep (0.1)


    screen.tracer(True)
    screen.exitonclick()

gameoflife()



