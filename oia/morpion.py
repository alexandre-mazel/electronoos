import copy
import random
import time
import numpy as np

def renderWaiting(durationSec=1.):
    timeBegin = time.time()
    speedAnimation = 0.05
    while time.time()-timeBegin<durationSec:
        print("-\r",end="")
        time.sleep(speedAnimation)
        print("\\\r",end="")
        time.sleep(speedAnimation)
        print("|\r",end="")
        time.sleep(speedAnimation)
        print("/\r",end="")
        time.sleep(speedAnimation)
    print("  ")
    
def pickMinRandomly(a):
    """
    pick one beyond minimal value in a list.
    return the index of the element
    """
    listMin = []
    m = np.min(a)
    for i,e in enumerate(a):
        if e == m:
            listMin.append(i)
    
    #~ print(m)
    #~ listMin = np.where(a==m)[0]
    return listMin[random.randint(0,len(listMin)-1)]
#~ print( pickMinRandomly([1,2,1,4]) )
    
def onlyonepositive(a):
    """
    return True if there's only one positive in list a
    """
    nbr = 0
    for e in a:
        if e >= 0: 
            nbr += 1
            if nbr>1: return False
    return nbr==1


class Game:
    def __init__(self,w=3,h=3):
        self.cpuManager = None
        if 0:
            # morpion
            self.bGravity = False
            self.nNbrAligned = 3
        else:
            # puissance 4
            self.bGravity = True
            self.nNbrAligned = 4
            w = 7
            h = 6
            
        self.w = w
        self.h = h
        self.startNewGame()
        
    def registerCpu(self,cpuObj):
        self.cpuManager = cpuObj
        
    def getCpuManager(self):
        return self.cpuManager
        
    def startNewGame(self):
        self.world = []
        # the world is made of 0: empty, 1: player one, 2: player tow
        for j in range(self.h):
            self.world.append([])
            for i in range(self.w):
                self.world[j].append(0)

    
    def drawBoard(self):
        print("  ",end="")
        for j in range(len(self.world[0])):
            print("%d " % (j+1),end="")
        print("")
            
        for j,line in enumerate(self.world):
            print("%d " % (j+1),end="")
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
        if self.bGravity:
            j = 0
            for i in range(self.w):
                if self.world[j][i] == 0:
                        possible.append((i,j))
        else:
            for j in range(self.h):
                for i in range(self.w):
                    if self.world[j][i] == 0:
                        possible.append((i,j))
        return possible
        
    def findAligned(self,nbr_aligned):
        """
        look for an alignment of nbr_aligned in vertic, horiz or diag
        return 0 if no one, symbol of aligned if aligned, 3 if drawgame
        """
        bVerbose = 0
        # horiz:
        for j in range(self.h):
            nPrev = -1
            nConsecutive = 0
            for i in range(self.w):
                val = self.world[j][i]
                if val == nPrev:
                    nConsecutive += 1
                    if nConsecutive == nbr_aligned and val != 0:
                        return val
                else:
                    nPrev = val
                    nConsecutive = 1
                    
        # vertic:
        for i in range(self.w):
            nPrev = -1
            nConsecutive = 0
            for j in range(self.h):
                val = self.world[j][i]
                if val == nPrev:
                    nConsecutive += 1
                    if nConsecutive == nbr_aligned and val != 0:
                        return val
                else:
                    nPrev = val
                    nConsecutive = 1
                    
        # for diags we decide of a starting point then we decay
        # diag \
        for j in range(self.h-nbr_aligned+1):
            for i in range(self.w-nbr_aligned+1):
                k = 0
                nPrev = -1
                nConsecutive = 0
                while 1:
                    if bVerbose: print("DBG: findAligned diag \: testing %d,%d" % (i+k,j+k))
                    try:
                        val = self.world[j+k][i+k]
                    except IndexError:break
                    
                    if val == nPrev:
                        nConsecutive += 1
                        if nConsecutive == nbr_aligned and val != 0:
                            return val
                    else:
                        nPrev = val
                        nConsecutive = 1
                    k += 1
                    
        # diag /
        for j in range(self.h-nbr_aligned+1):
            for i in range(nbr_aligned-1,self.w):
                k = 0
                nPrev = -1
                nConsecutive = 0
                while 1:
                    if bVerbose: print("DBG: findAligned diag /: testing %d,%d" % (i-k,j+k))
                    try:
                        if i-k<0:
                            break
                        val = self.world[j+k][i-k]
                    except IndexError:break
                    
                    if val == nPrev:
                        nConsecutive += 1
                        if nConsecutive == nbr_aligned and val != 0:
                            return val
                    else:
                        nPrev = val
                        nConsecutive = 1
                    k += 1

                    
        return 0
        
    def _getWinnerInternal(self):
        if len(self.getPossibleAction()) < 1:
            return 3
        return self.findAligned( self.nNbrAligned )
        
        
    
    def _getWinnerInternalMorpion(self):
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
                print("A toi humain de jouer: entre une colonne (1..%d):" % self.w)
                col = int(input())-1
                if not self.bGravity:
                    print("et maintenant une ligne (1..%d):" % self.h)
                    line = int(input())-1
                else:
                    line = 0
                break
            except ValueError as err:
                print("Erreur, recommence (%s)" % str(err))
        return col, line
        
    def askRandomPlayer(self,possibleMove):
        return possibleMove[random.randint(0,len(possibleMove)-1)]
        
    def askCpu(self,possibleMove, nPlayerNum):
        if self.cpuManager == None:
            return possibleMove[0]
        return self.cpuManager.getAction(self.world,possibleMove,nPlayerNum)
        
    def receiveMove(self,pos,numPlayer,bSimulate=False):
        """
        return True if move is leggit
        """
        #~ print("INF: Game.receiveMove: receive for player %d, pos: %s" % (numPlayer,str(pos)))
        
        if not self.bGravity:
            finalPos = pos[:]
        else:
            finalPos = [pos[0]]
            alt = 0
            if finalPos[0]<0 or finalPos[0]>=self.w:
                return False
            while self.world[alt][finalPos[0]] == 0:
                alt += 1
                if alt >= self.h:
                    break
            finalPos.append(alt-1)
            #~ print("receiveMove: gravity: finalPos: %s" %str(finalPos))
        
        try:
            content = self.world[finalPos[1]][finalPos[0]]
        except IndexError: return False
        
        if content != 0:
            return False
            
        if self.cpuManager != None and not bSimulate: self.cpuManager.storeAction(self.world,pos,numPlayer)
        
        self.world[finalPos[1]][finalPos[0]] = numPlayer
        return True
        
    def mc(self,nNumPlayerToPlay,nDepth=4, bFirstCall = True):
        """
        calcul les gains pour le joueur 1, de toutes les combinaisons depuis le jeu actuel.
        Si bFirstCall: retourne le gain, suivi d'un tableau des gains pour chaque actions possible
        - nNumPlayerToPlay: numero du prochain joueur a jouer: 1 ou 2
        - nDepth: profondeur de recherche
        """
        #~ if 0:
            #~ print("DBG: mc: world depth: %d, nNumPlayerToPlay: %d" % (nDepth,nNumPlayerToPlay) )
            #~ self.drawBoard()
        winner = self._getWinnerInternal()
        if winner != 0:
            gain = [1,-1,0]
            pts = (gain[winner-1])*pow(self.w,nDepth)
            if 0:
                self.drawBoard()
                print("DBG: mc victory depth: %d, pts: %d" % (nDepth,pts))
            return pts
            
        if nDepth == 0:
            return 0
            
        dupWorld = copy.deepcopy(self.world)
        
        actions = self.getPossibleAction()
        sum = 0
        nextPlayer = ((nNumPlayerToPlay-1+1)%2)+1
        if bFirstCall:
            scorePerActions = []
        for act in actions:
            self.receiveMove(act,nNumPlayerToPlay,bSimulate=True)
            res = self.mc(nextPlayer,nDepth-1,bFirstCall=False)
            sum += res
            if bFirstCall: scorePerActions.append(res)
            self.world = copy.deepcopy(dupWorld)
        # last loop iteration, we have restaured world state
        if bFirstCall:
            print("INF: mc: actions: %s" % actions)
            print("INF: mc: scorePerActions: %s" % scorePerActions)
            return sum, scorePerActions
        return sum
        
        
            
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
        
global_game = Game()

def runGame(bBatch=False, bRepetitiveHuman=False,bFirstPlayerIsHuman=True,bQuiet=False):
    """
    - bFirstPlayerIsHuman: else it's an ai
    """
    bFirstPlayerIsRandomAI = False
    #~ bFirstPlayerIsRandomAI = True
    
    bActivateMc = False
    bActivateMc = True
    
    if bActivateMc:
        print("choisis un niveau d'IA: 1..5")
        nMcLevel = int(input())
        if nMcLevel < 1: nMcLevel = 1
        if nMcLevel > 7: nMcLevel = 7
        nMcLevel += 1 # mc is 2..6 (7 is *long*)
        aMcHistory = []
    
    if bRepetitiveHuman:
        aAutomaticHumanChoice = [(0,0),(1,1),(2,2),(1,0),(2,0),(0,1),(0,2),(1,2)] # help debugging: faster and reproducible
    else:
        aAutomaticHumanChoice = []
        
    nIdxAutomaticHumanChoice = 0
    g = global_game
    if 1:
        if g.getCpuManager() == None:
            #~ import ai_cpu_random as ai_cpu
            import ai_cpu as ai_cpu
            cpu_name = "toto" # first ai trained
            cpu_name = "fight_random" # ai trained against pure random player
            cpu_name = "dumb" # very few trained ai, train only against real human
            ai = ai_cpu.AiCpu(cpu_name)
            g.registerCpu(ai)
            if bBatch: g.getCpuManager().bAutosave = False
    g.startNewGame()
    if not bQuiet: g.drawBoard()
    while 1:
        mc_res = g.mc(1,4)
        print("mc%d: %s" % (4,str(mc_res)) )
        if mc_res[0]<0 and onlyonepositive(mc_res[1]):
            amsg = ["huhuhu", "hihihi", "hunhun"]
            msg = amsg[random.randint(0,len(amsg)-1)]
            print("\n AI says: %s !!!\n" % msg)
        if bFirstPlayerIsHuman:
            while 1:
                if nIdxAutomaticHumanChoice < len(aAutomaticHumanChoice):
                    pos = aAutomaticHumanChoice[nIdxAutomaticHumanChoice];nIdxAutomaticHumanChoice+=1
                else:
                    pos = g.askPlayer()
                ret = g.receiveMove(pos,1)
                if ret: break
                print("coup impossible, re-essaye encore")
        else:
            if bFirstPlayerIsRandomAI:
                pos = g.askRandomPlayer(g.getPossibleAction())
            else:
                pos = g.askCpu(g.getPossibleAction(),1)
            g.receiveMove(pos,1)
        if not bQuiet: g.drawBoard()      
        n = g.getWinner()
        if handleEnd(n):
            break
            
        if not bQuiet: 
            print("AI is thinking...")
        timeBegin = time.time()
        if bActivateMc:
            mc_res = g.mc(2,nMcLevel) # between 2 and 6
            print("mc%d: %s (duration: %.1fs)" % (nMcLevel,str(mc_res),time.time()-timeBegin) )
            aMcHistory.append(mc_res[0])
            print("aMcHistory: %s" % str(aMcHistory) )
        
        if 1: renderWaiting()      
        
        if not bActivateMc:
            pos = g.askCpu(g.getPossibleAction(),2)
        else:
            # use mc:
            #~ sol = np.argmin(mc_res[1]) # pb si tous a zero => full gauche
            sol = pickMinRandomly(mc_res[1])
            #~ print("ai sol: %s" % sol)
            pos = g.getPossibleAction()[sol]
        g.receiveMove(pos,2)
        if not bQuiet: g.drawBoard()
        n = g.getWinner()
        if handleEnd(n):
            break
    return n

def runBatch(nbr_game=1000):
    timeBegin = time.time()
    bFirstPlayerIsHuman = 1
    bFirstPlayerIsHuman = 0
    listWinner = [0,0,0]
    for i in range(nbr_game):
        print("game %d/%d" % (i,nbr_game))
        winner = runGame(bBatch=True, bRepetitiveHuman=True,bFirstPlayerIsHuman=bFirstPlayerIsHuman,bQuiet=True)
        listWinner[winner-1] += 1

    print("")
    print("win human: %.2f" % int(listWinner[0]*100./nbr_game) )
    print("win cpu: %.2f" % int(listWinner[1]*100./nbr_game) )
    print("draw: %.2f" % int(listWinner[2]*100./nbr_game) )
    
    
    global_game.getCpuManager().save()
    
    duration = time.time()-timeBegin
    print("INF: duration per 100 games: %.1f" % (duration*100/nbr_game) )
    return listWinner
# runBatch - end

def runVisioBatch():
    import matplotlib.pyplot as plt
    import numpy as np

    playPerBatch = 100000
    histHuman = []
    histCpu = []
    histDraw = []
    nbr_batch = 10
    for i in range(nbr_batch):
        print("#"*160)
        print("batch %d/%d" % (i,nbr_batch))
        listWinner = runBatch(playPerBatch)
        histHuman.append(listWinner[0])
        histCpu.append(listWinner[1])
        histDraw.append(listWinner[2])

    print("histHuman: %s" % histHuman)
    print("histCpu: %s" % histCpu)
    print("histDraw: %s" % histDraw)
    xaxis = range(len(histHuman))
    yaxis1 = np.array(histHuman)
    yaxis2 = np.array(histCpu)
    yaxis3 = np.array(histDraw)

    plt.plot(xaxis,yaxis1)
    plt.plot(xaxis,yaxis2)
    plt.plot(xaxis,yaxis3)
    plt.legend(['human', 'cpu', "draw"], loc='upper left')
    plt.show()
    plt.savefig('/tmp/ai_evolution_%s.png' % time.time())
    time.sleep(2.)  # time to save fig ?

    

#~ runBatch(1000)
#~ runVisioBatch()
runGame()
"""
Win tricks:

 1 2 3 4 5 6 7
1 . . . . . . .
2 . . . . . . .
3 X . . . . . .
4 O . O O . . .
5 O . X X X . .
6 O X X X O . .
AI is thinking...
INF: mc: actions: [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
INF: mc: scorePerActions: [6360, -132, 6392, 2679, 6544, 9602, 6619]
mc: (38064, [6360, -132, 6392, 2679, 6544, 9602, 6619])

  1 2 3 4 5 6 7
1 O . O O . O O
2 X . X X . X X
3 X . O X . O X
4 O . X O . X O
5 O . X X . X O
6 X X O X . O O
AI is thinking...
INF: mc: actions: [(1, 0), (4, 0)]
INF: mc: scorePerActions: [15092, 33614]
mc7: (48706, [15092, 33614]) (duration: 0.0s)
aMcHistory: [20262, 8164, 42340, 30833, -4747, 3841, 32403, 81477, 74434, 90539, 65190, 46932, 41032, 35388, 30044, 48706]

cpu win:
  1 2 3 4 5 6 7
1 . . O X . O X
2 . X X O . X O
3 . O O O . O X
4 . X X O . X X
5 O O X X . X X
6 X O O X . O O
AI is thinking...
INF: mc: actions: [(0, 0), (1, 0), (4, 0)]
INF: mc: scorePerActions: [76832, -24010, 76832]
mc8: (129654, [76832, -24010, 76832]) (duration: 0.0s)
aMcHistory: [371124, 223169, 691912, 617220, 142574, 351585, 188454, 276423, 114364, 73874, 80440, 45116, 366992, -901, 205996, 129654]
"""

