import random

class AiCpu:
    """
    the AI to learn how to play to any game.
    """
    def __init__( self, name ):
        self.name = name
        
    def storeMove(self, world,move,num_player):
        """
        optionnaly store move of one player during a game to analyse them further
        - world: state of the world (before move occurs)
        - num_player: player who do the move
        """
        pass
        
    def getMove(self,world,possible_move):
        """
        return the move to do among possibles one 
        based on a state of the world.
        - world: state of the world
        - possible_move: list of possible move :)
        """
        return possible_move[random.randint(0,len(possible_move)-1)]
        
    def updateStats(self,num_winner):
        """
        at the end of a game, take some decisions about 
        what could have been made better and memorize them
        - num_winner: player who wins this game
        """
        pass
        
        
# class AiCpu - end