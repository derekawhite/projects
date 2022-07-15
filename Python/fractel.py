from turtle import Turtle, Screen
import random
from random import randint
import time
from datetime import datetime
import time

from matplotlib import image
from matplotlib import pyplot as plt


def plot1(max):
    random.seed(time.time())
 
    screen = Screen()
    screen.setup(800,800)
    
    # set turtle screen title
    screen.title("Turtle Window For xxx")

    width, height = screen.window_width(), screen.window_height()

    x1, y1 = -width/2 + 1, -height/2 + 1
    x2, y2 = width/2 - 1, -height/2 + 1
    x3, y3 = 1, height/2 - 1

    x, y = x1, y1

    turtle = Turtle(visible=False)
    turtle.speed(0)
    turtle.penup()

    startt = datetime.now()

    for index in range(max):
        turtle.setposition(x,y)
        turtle.dot(3, 'black')

        dir = randint (1, 3)

        if (dir == 1):
            x = x + (x1 - x)/2
            y = y + (y1 - y)/2
        elif (dir == 2):
            x = x + (x2 - x)/2
            y = y + (y2 - y)/2
        elif (dir == 3):
            x = x + (x3 - x)/2
            y = y + (y3 - y)/2

        if index % 100 == 0:
            endt = datetime.now()
            diff = endt - startt

            screen.title(f"{index} of {max}. Time: {diff}")

    screen.exitonclick()

def plot2(max):
    figure, axes = plt.subplots()
    
    axes.set_aspect( 1 )

    plt.xlim(0, 100)
    plt.ylim(0,100)

    width, height = 100, 100

    x1, y1 =  1, 1
    x2, y2 = width - 1, 1
    x3, y3 = width/2, height - 1

    x, y = x1, y1
    startt = datetime.now()

    for index in range(max):

        dir = randint (1, 3)

        if (dir == 1):
            x = x + (x1 - x)/2
            y = y + (y1 - y)/2
        elif (dir == 2):
            x = x + (x2 - x)/2
            y = y + (y2 - y)/2
        elif (dir == 3):
            x = x + (x3 - x)/2
            y = y + (y3 - y)/2

        c = plt.Circle((x , y), 0.2 )
        axes.add_artist(c)

    endt = datetime.now()
    diff = endt - startt

    plt.title( f"{max}. Time: {diff}" )
    plt.show()


#max = int(input ("Number of points:"))
max = 10000
plot1(max)
#plot2(max)
