import random

class AiCpu:
    def __init__( self, name ):
        self.name = name
        
    def storeMove(self, world,move,num_player):
        pass
        
    def getMove(self,world,possible_move):
        return possible_move[random.randint(0,len(possible_move)-1)]
        
    def updateStats(self,num_winner):
        pass
        
        
# class AiCpu - end