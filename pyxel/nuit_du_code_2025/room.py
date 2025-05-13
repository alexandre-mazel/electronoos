import pyxel

import terrain
from terrain import kTypeGrass, kTypeWall, kTypeFire, kTypeDoor, kTypeSlip

import time

class Room:
    def __init__( self ):
        self.size_tile = 16
        self.reset()
        
    def reset( self ):
        self.world = [] # liste 2D x*y
        self.offsetx = 0 # position haut gauche de la partie affiche dans la carte
        self.offsety = 0
        self.timeStartScroll = 0
        self.inc_scroll = 1
        
        
    def create( self, w = 1024, h = 1024 ):
        self.reset()
        if 0:
            # carte de test
            self.w = w
            self.h = h
            for j in range( h ):
                self.world.append([])
                for i in range( w ):
                    case = kTypeGrass
                    if (i+j*5)%11==0:
                        case = kTypeWall
                    self.world[-1].append(case)
                    
            self.world[6][6] = kTypeFire
        else:
            self.create_from_terrain(0)
        
    def create_from_terrain( self, num_terrain ):
        print("DBG: create_from_terrain: num_terrain: %d" % num_terrain )
        self.reset()
        self.world = terrain.get_terrain(num_terrain)
        self.w = len(self.world[0])
        self.h =  len(self.world)
                
                
    def conv_global_to_local( self, x, y ):
        """
        convertit des coord de la carte global dans la partie locale actuellement a l'ecran
        """
        return int(x-self.offsetx+0.5),int(y-self.offsety+0.5)
        
    def get_case_at( self, x, y ):
        return self.world[(y+14)//self.size_tile][(x+8)//self.size_tile]
        
    def is_passable( self, x, y ):
        """
        is_passable, x et y en coordonnees monde
        """
        #~ print("DBG: is_passable: x: %s, y: %s" %  (x,y) )
        
        if x < 0:
            return False
        if y < 0:
            return False

        if x >= self.w*self.size_tile:
            return False
        if y >= self.h*self.size_tile:
            return False
           
        case = self.get_case_at( x, y )
        #~ print("DBG: is_passable: case: %s" %  case )
        if case == kTypeWall:
            return False
            
        return True
        
    def get_empty_space( self ):
        """
        retourne le x et y monde d'une zone libre sur la carte plutot qui ne serait pas en haut a gauche
        """
        while 1:
            x = pyxel.rndi(3,self.w-1)
            y = pyxel.rndi(3,self.h-1)
            if self.is_passable(x*self.size_tile,y*self.size_tile):
                return x*self.size_tile,y*self.size_tile
            print("DBG: get_empty_space: looping (tested: %d,%d)..." % (x,y))
        assert(0)
        return 1,1
        
    def update( self, heros_x, heros_y ):
        
        # handle door
        case = self.get_case_at( heros_x, heros_y )
        if case >= kTypeDoor:
            num_terrain = case-kTypeDoor
            self.create_from_terrain(num_terrain)
            return True
        
        # update camera
        scroll = 0
        if heros_x-self.offsetx > 60:
            self.offsetx += self.inc_scroll
            scroll = 1
        elif heros_x-self.offsetx < 40:
            self.offsetx -= self.inc_scroll
            scroll = 1
            if self.offsetx < 0:
                self.offsetx = 0
        if heros_y-self.offsety > 60:
            self.offsety += self.inc_scroll
            scroll = 1
        elif heros_y-self.offsety < 40:
            self.offsety -= self.inc_scroll      
            scroll = 1
            if self.offsety < 0:
                self.offsety = 0
             
        if 0:
            # camera scroll elastique
            if scroll == 1:
                if self.timeStartScroll == 0:
                    # first frame scrolling
                    self.timeStartScroll = time.time()
                elif time.time()-self.timeStartScroll:
                    self.inc_scroll *= 1.1
                    if self.inc_scroll > 4:
                        self.inc_scroll = 4
            else:
                self.inc_scroll = 0.1
        else:
            # camera lineaire
            self.inc_scroll = 2
        
            
                
        return False
        
    def render( self ):
        
        coordToGraph = { # kType => coord in pyxres
            kTypeGrass: [0,112],
            kTypeWall: [0,96],
            kTypeFire: [0,128],
            kTypeDoor: [0,144],
            kTypeSlip: [144,32],
        }
        
        nbr_tile_per_screen = 8
        transp_color = 2
        bank = 0
        size_tile = self.size_tile
        
        for j in range( nbr_tile_per_screen + 1): # +1 pour des cases partiels
            for i in range( nbr_tile_per_screen + 1 ):
                case_x = i+int(self.offsetx/size_tile)
                case_y = j+int(self.offsety/size_tile)
                #~ print("DBG: room.render: case_x: %d, case_y: %d" % ( case_x, case_y ) )
                if case_x >= self.w or case_y >= self.h :
                    case = kTypeGrass
                else:
                    #~ print(self.world)
                    case = self.world[case_y][case_x]
                    if case >= kTypeDoor and case < kTypeDoor+26:
                        case = kTypeDoor
                if case == kTypeSlip:
                    # rend une herbe sous le slip
                    u,v = coordToGraph[kTypeGrass]
                    pyxel.blt(i*size_tile-self.offsetx%size_tile, j*size_tile-self.offsety%size_tile, bank, u, v, size_tile,size_tile,transp_color)

                u,v = coordToGraph[case]
                #u += (i%2)*16
                pyxel.blt(i*size_tile-self.offsetx%size_tile, j*size_tile-self.offsety%size_tile, bank, u, v, size_tile,size_tile,transp_color)
        
# class Room - end

def autotest():
    room = Room()
    room.create()
    room.update()
        
        
if __name__ == "__main__":
    autotest()