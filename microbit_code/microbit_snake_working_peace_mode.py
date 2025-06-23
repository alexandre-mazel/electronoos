from microbit import *
import random
import music

H = W = 5 # size of screen

class Snake:
    def __init__( self ):
        self.reset()

    def reset( self ):
        self.pt = [[2,2]]
        self.v_for_dir = [(1,0),(0,1), (-1,0),(0,-1)] # speed of each direction
        self.dir = 0 # what direction
        self.create_egg()
        self.time_sleep = 800;
        
    def create_egg( self ):
        self.egg = (random.randint(0,W-1),random.randint(0,H-1))

    def update( self ):

        if self.egg[0] == self.pt[0][0] and self.egg[1] == self.pt[0][1]:
            self.pt.append( [ self.pt[-1][0],self.pt[-1][1] ] ) # dup the last
            self.create_egg()
            audio.play(Sound.SLIDE, wait=False)
            
    

        # decale la queue
        for i in range(len(self.pt)-1, 0,-1):
            self.pt[i] = self.pt[i-1][:]
            
        
        if button_a.was_pressed():
            self.dir -= 1
            self.dir = self.dir%(len(self.v_for_dir))
            
        if button_b.was_pressed():
            self.dir += 1
            self.dir = self.dir%(len(self.v_for_dir))
        
        for i in range(len(self.pt[0])):
            self.pt[0][i] += self.v_for_dir[self.dir][i]
        self.pt[0][0] %= H;
        self.pt[0][1] %= W;
        

    def output( self ):
        print( "pt:", self.pt )
        print( "v_for_dir:", self.v_for_dir )
        print( "dir:", self.dir )
        print( "egg:", self.egg )
        print( "time_sleep:", self.time_sleep )
        
    def render( self ):
        display.clear()
        
        display.set_pixel(self.egg[0],self.egg[1],4) # before the snake so it doesn't overide the rendering of the snake

        # draw snake (from the end so even in peace mode, we saw the head)
        for i in range(len(self.pt)-1,-1,-1):
            col = 9
            if i > 0:
                col = 7
            display.set_pixel(self.pt[i][0],self.pt[i][1],col)

        sleep( self.time_sleep )
        if self.time_sleep > 100:
            self.time_sleep -= 1

        
    

snake = Snake()
while 1:
    snake.update()
    snake.output()
    snake.render()

