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
        return 0 if no one, 1 if player 1 win, or 2 if player 2 win, 3 if drawgame
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
                
        if len(self.getPossibleAction()) < 1:
            return 3
            
        return 0
        
    def getWinner(self):
        win = self._getWinnerInternal()
        if win != 0 and self.cpuManager != None:
            if win != 3:
                self.cpuManager.updateStats(win,2)

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
        return self.cpuManager.getAction(self.world,possibleMove,2)
        
    def receiveMove(self,pos,numPlayer):
        """
        return True if move is leggit
        """
        print("INF: Game.receiveMove: receive for player %d, pos: %s" % (numPlayer,str(pos)))
        
        try:
            content = self.world[pos[1]][pos[0]]
        except IndexError: return False
        
        if content != 0:
            return False
        if self.cpuManager != None: self.cpuManager.storeAction(self.world,pos,numPlayer)
        self.world[pos[1]][pos[0]] = numPlayer
        return True
# class Game - end

def handleEnd(winner):
    """
    return True if game is finished
    """
    if winner != 0:
        if winner == 1: print("human win")
        if winner == 2: print("cpu win")
        if winner == 3: print("draw game")
        return True
    return False
            
def runGame(bRepetitiveHuman=False):
    if bRepetitiveHuman:
        aAutomaticHumanChoice = [(0,0),(1,1),(2,2),(1,0),(2,0),(0,1),(0,2),(1,2)] # help debugging: faster and reproducible
    else:
        aAutomaticHumanChoice = []
        
    nIdxAutomaticHumanChoice = 0
    g = Game()
    if 1:
        #~ import ai_cpu_random as ai_cpu
        import ai_cpu as ai_cpu
        ai = ai_cpu.AiCpu("toto")
        g.registerCpu(ai)
    g.drawBoard()
    while 1:
        while 1:
            if nIdxAutomaticHumanChoice < len(aAutomaticHumanChoice):
                pos = aAutomaticHumanChoice[nIdxAutomaticHumanChoice];nIdxAutomaticHumanChoice+=1
            else:
                pos = g.askPlayer()
            ret = g.receiveMove(pos,1)
            if ret: break
            print("coup impossible, re-essaye encore")
        g.drawBoard()
        n = g.getWinner()
        if handleEnd(n):
            break

        pos = g.askCpu(g.getPossibleAction())
        g.receiveMove(pos,2)
        g.drawBoard()
        n = g.getWinner()
        if handleEnd(n):
            break
    return n

def runBatch(nbr_game=100):
    listWinner = [0,0,0]
    for i in range(nbr_game):
        winner = runGame(bRepetitiveHuman=True)
        listWinner[winner-1] += 1

    print("win human: %d" % listWinner[0])
    print("win cpu: %d" % listWinner[1])
    print("draw: %d" % listWinner[2])
    
#~ runBatch()
runGame()
