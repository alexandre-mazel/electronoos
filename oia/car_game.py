import chrono
import msvcrt
import random
import time

def game_car():
    c = chrono.Chrono()
    time.sleep(random.random()*4)
    while msvcrt.kbhit():
        # Only if there's a keypress waiting do we get it with getch()
        print("Key hit! ({})".format(msvcrt.getch()))
    c.start()
    input("La voiture de devant freine, vite freine toi aussi, en pressant enter!")
    c.stop()
    print("Temps pour freiner: %.2fs" % c.get_elapsed_time())


while 1:
    game_car()