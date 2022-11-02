import turtle
import time
from datetime import datetime

screen = turtle.Screen()
screen.title("Clock")
screen.setup(425, 425)

second_hand = turtle.Turtle()
minute_hand = turtle.Turtle()
hour_hand = turtle.Turtle()

second_hand.pensize(1)
second_hand.hideturtle()
second_hand.speed(10)
second_hand.color("red")
second_hand.left(90)

minute_hand.pensize(2)
minute_hand.hideturtle()
minute_hand.speed(10)
minute_hand.left(90)

hour_hand.pensize(4)
hour_hand.hideturtle()
hour_hand.speed(10)
hour_hand.left(90)

while True:
    start = datetime.now()
    
    
    second_hand.clear()
    minute_hand.clear()
    hour_hand.clear()

    second_hand.right(6)
    second_hand.forward(200)
    second_hand.backward(200)
    
    minute_hand.right(.06)
    minute_hand.forward(190)
    minute_hand.backward(190)
    
    hour_hand.right(.006)
    hour_hand.forward(135)
    hour_hand.backward(135)
    
    #~ time.sleep(1)

    
    end = datetime.now()

    
    total = end - start
    
    time.sleep(1-total.total_seconds()-0.01)
    
    print("time process: %.2f" % total.total_seconds())
    print("time loop: %.2f" % (datetime.now()- start).total_seconds())