

class Game:
    def __init__(self):
        self.startNewGame()
        self.cpuManager = None
        
    def registerCpu(self,cpuObj):
        self.cpuManager = cpuObj
        
    def startNewGame(self,w=3,h=3):
        self.world = []
        # the world is made of 0: empty, 1: player one, 2: player tow
        for j in range(h):
            self.world.append([])
            for i in range(w):
                self.world[j].append(0)
                
        self.w = w
        self.h = h
    
    def drawBoard(self):
        for line in self.world:
            for case in line:
                if case == 0:
                    c = '.'
                elif case == 1:
                    c = 'X'
                else:
                    c = 'O'
                print("%s " % c, end="")
            print("")
            
    def getPossibleAction(self):
        """
        return a list of possible action as pair (x,y)
        num_player is 1 or 2
        """
        possible = []
        for j in range(self.h):
            for i in range(self.w):
                if self.world[j][i] == 0:
                    possible.append((i,j))
        return possible
        
    
    def _getWinnerInternal(self):
        """
        compute if someone has won.
        return 0 if no one, 1 if player 1 win, or 2 if player 2 win
        """
        # lazy code: work only for 3x3
        # horiz:
        for i in range(len(self.world)):
            if self.world[i][0] == 0:
                continue
            if self.world[i][0] == self.world[i][1] == self.world[i][2]:
                return self.world[i][0]
                
        # vertic:
        for j in range(len(self.world)):
            if self.world[0][j] == 0:
                continue
            if self.world[0][j] == self.world[1][j] == self.world[2][j]:
                return self.world[0][j]
                
        # diago
        if self.world[1][1] != 0:
            if self.world[0][0] == self.world[1][1] == self.world[2][2]:
                return self.world[0][0]
            if self.world[0][2] == self.world[1][1] == self.world[2][0]:
                return self.world[0][2]    
        return 0
        
    def getWinner(self):
        win = self._getWinnerInternal()
        if win != 0 and self.cpuManager != None:
            self.cpuManager.updateStats(win)

        return win

    def askPlayer(self):
        """
        return une paire (col, line)
        """
        while 1:
            try:
                print("A toi humain de jouer: entre une colonne (1..3):")
                col = int(input())-1
                print("et maintenant une ligne (1..3):")
                line = int(input())-1
                break
            except ValueError as err:
                print("Erreur, recommence (%s)" % str(err))
        return col, line
        
    def askCpu(self,possibleMove):
        if self.cpuManager == None:
            return possibleMove[0]
        return self.cpuManager.getMove(self.world,possibleMove)
        
    def receiveMove(self,pos,numPlayer):
        """
        return True if move is leggit
        """
        print("INF: Game.receiveMove: receive for player %d, pos: %s" % (numPlayer,str(pos)))
        content = self.world[pos[1]][pos[0]]
        if content != 0:
            return False
        if self.cpuManager != None: self.cpuManager.storeMove(self.world,pos,numPlayer)
        self.world[pos[1]][pos[0]] = numPlayer
        return True
# class Game - end

def runGame():
    g = Game()
    if 1:
        import ai_cpu
        ai = ai_cpu.AiCpu("toto")
        g.registerCpu(ai)
    g.drawBoard()
    while 1:
        while 1:
            pos = g.askPlayer()
            ret = g.receiveMove(pos,1)
            if ret: break
            print("coup impossible, re-essaye encore")
        g.drawBoard()
        n = g.getWinner()
        if n != 0:
            print("human win")
            break
        pos = g.askCpu(g.getPossibleAction())
        g.receiveMove(pos,2)
        g.drawBoard()
        n = g.getWinner()
        if n != 0:
            print("cpu win")
            break


runGame()