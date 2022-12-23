import random
import json
import copy

def chooseWeighted(a):
    """
    pick an element among a list of weighted choice. (weight are not to be necessarily sorted)
    return the index of the element
    """
    print("DBG: chooseWeighted: list: " + str(a) )
    sum_weight = sum(a)
    c = random.random()*sum_weight
    print("DBG: chooseWeighted: choose: %.3f" % c )
    accu = 0
    for i,val in enumerate(a):
        accu += val
        if accu > c:
            print("DBG: chooseWeighted: pick: %s" % i )
            return i
    assert(0)

def posStringToPos(s):
    """
    convert a string "(1,2)" to a tuple (1,2)
    """
    s = s.replace("(","").replace(")","")
    a = s.split(",")
    for i in range(len(a)):
        a[i] = int(a[i])
    return tuple(a)
    
class AiCpu:
    """
    an AI to learn how to play to any game.
    """
    def __init__( self, name ):
        self.name = name
        print("INF: AiCpu: initialising train ai nammed '%s'"  % name )
        self.strSaveFilename = "/save/ai_%s.dat" % name
        self.mem = {} # for each (world, num_player) a dict of action => the previous success chance: [-1.,+1.]: -1: bad, +1: good, 0: neutral
        self.currentActions = [] # store all world and actions of each player (world,num_player,action)
        self.load()
        
    def save(self):
        print("INF: saving to '%s'" % self.strSaveFilename)
        f = open(self.strSaveFilename,"wt")
        ret = json.dump((self.mem),f,indent=2, ensure_ascii=False)
        f.close()
        
    def load(self):
        print("INF: loading from '%s'" % self.strSaveFilename)
        try:
            f = open(self.strSaveFilename,"rt")
            dictlist = json.load(f)
            self.mem = dictlist
            f.close()      
        except FileNotFoundError: pass
        
    @staticmethod
    def _getKeySituation(world, num_player):
        return "%s__%s" % (str(world),num_player)

    @staticmethod
    def _getKeyAction(action):
        return "%s" % (str(action))
        
    def _assumeExist( self, k ):
        if k in self.mem: return
        self.mem[k] = dict()


    #~ def update(self, world, num_player, action):
        #~ k = self._getKeySituation(world, num_player, action)                                                                                    
        #~ self._assumeExist(k)
        #~ self.dictProg[k] = self.dictProg[k]*rate+action*(1-rate)
        #~ return 
        
        
    def storeAction(self, world,action,num_player):
        """
        optionnaly store action of one player during a game to analyse them further
        - world: state of the world (before action occurs)
        - num_player: player who do the action
        """
        self.currentActions.append((copy.deepcopy(world),num_player,action))
        
    def getAction(self,world,possible_action,num_player):
        """
        return the move/action to do among possibles one 
        based on a state of the world.
        - world: state of the world
        - possible_action: list of possible move/action
        - num_player: num player of ai
        """
        k = self._getKeySituation(world, num_player)
        try:
            listKnown = self.mem[k]
        except KeyError as err:
            print("DBG: getAction: unknown situation => random (key:%s)" % str(err))
            return possible_action[random.randint(0,len(possible_action)-1)]
        
        print("DBG: getAction: listKnown: %s" % str(listKnown))            
        listKnownSortedKeys = sorted(listKnown,key = lambda x: x[1])
        print("DBG: getAction: listKnown sorted keys: %s" % str(listKnownSortedKeys))
        rSumPositive = 0
        allPositiveGain = []
        for i,k in enumerate(listKnownSortedKeys):
            potential_gain = listKnown[k]
            if potential_gain<=0:
                break
            allPositiveGain.append(potential_gain)
        print("DBG: getAction: allPositiveGain: %s" % str(allPositiveGain))
        if len(allPositiveGain) > 0:
            i = chooseWeighted(allPositiveGain)
            pos = listKnownSortedKeys[i]
            pos = posStringToPos(pos)
            print("DBG: getAction(1): pos: %s" % str(pos) )
            return pos
            
        # soit il y en a un dans la liste qui n'a jamais ete essayé, soit on prend le moins mauvais (randomly)
        listNotTested = []
        for act in possible_action:
            if self._getKeyAction(act) not in listKnown:
                listNotTested.append(act[:])
        print("DBG: getAction: listNotTested: %s" % str(listNotTested))
        if len(listNotTested) > 0:
            return listNotTested[random.randint(0,len(listNotTested)-1)]
            
        # choose among the negative one
        listKnownPositived = [1+v for v in listKnown.values()]
        print("DBG: getAction: listKnownPositived: %s" % str(listKnownPositived))
        print("DBG: getAction: listKnown: %s" % listKnown )
        i = chooseWeighted(listKnownPositived)
        pos = list(listKnown.keys())[i]
        print("DBG: getAction (2a): pos as str: %s" % pos )
        pos = posStringToPos(pos)
        print("DBG: getAction (2b): pos as tuple: %s" % str(pos) )
        return pos
        
                
        
    def updateStats(self,num_winner,num_player_ai):
        """
        at the end of a game, take some decisions about 
        what could have been made better and memorize them
        - num_winner: player who wins this game
        """
        print("DBG: updateStats: current actions: %s" % str(self.currentActions))
        print("DBG: updateStats: prev mem: %s" % str(self.mem))
            
        for num,a in enumerate(self.currentActions):
            world, num_player,action = a        
            if num_player==num_winner:
                gain = 1
            else:
                gain = -1
            k = self._getKeySituation(world, num_player)
            kAction = self._getKeyAction(action)
            try:
                prev = self.mem[k][kAction]
            except KeyError: prev = 0
            rate_new = max(0.01, num/len(self.currentActions))
            self._assumeExist(k)
            self.mem[k][kAction] = prev*(1-rate_new) + gain*rate_new
        
        print("DBG: updateStats: new mem: %s" % str(self.mem))
        self.save()
        
        
# class AiCpu - end