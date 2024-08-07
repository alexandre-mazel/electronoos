import random
import json
import copy
import gzip
import pickle

import sys
sys.path.append("../alex_pytools/")
import misctools

def chooseWeighted(a):
    """
    pick an element among a list of weighted choice. (weight are not to be necessarily sorted)
    return the index of the element
    """
    return chooseWeightedSquared(a)
    bVerbose = 0
    if bVerbose: print("DBG: chooseWeighted: list: " + str(a) )
    sum_weight = sum(a)
    if sum_weight < 0.001:
        # pure random
        return random.randint(0,len(a)-1)
    c = random.random()*sum_weight
    if bVerbose: print("DBG: chooseWeighted: choose: %.3f" % c )
    accu = 0
    for i,val in enumerate(a):
        accu += val
        if accu > c:
            if bVerbose: print("DBG: chooseWeighted: pick: %s" % i )
            return i
    assert(0)
    
def chooseWeightedSquared(a):
    """
    pick an element among a list of weighted choice. (weight are not to be necessarily sorted)
    return the index of the element
    version squared to set enhance difference
    """
    #~ bVerbose = 1
    bVerbose = 0
    
    if bVerbose: print("DBG: chooseWeightedSquared: list: " + str(a) )
    a = [x*x for x in a]
    
    if bVerbose: print("DBG: chooseWeightedSquared: list squared: " + str(a) )
    sum_weight = sum(a)
    if sum_weight < 0.001:
        # pure random
        return random.randint(0,len(a)-1)
    c = random.random()*sum_weight
    if bVerbose: print("DBG: chooseWeightedSquared: choose: %.3f" % c )
    accu = 0
    for i,val in enumerate(a):
        accu += val
        if accu > c:
            if bVerbose: print("DBG: chooseWeightedSquared: pick: %s" % i )
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
        self.bUsePickle = 1
        self.load()
        self.bAutosave = True

        
    def save(self):
        print("INF: saving to '%s'" % self.strSaveFilename)
        misctools.backupFile(self.strSaveFilename)
        print("INF: saving %d situation(s)" % len(self.mem) )
        if 1:
            nSumActions = 0
            for k,v in self.mem.items():
                nSumActions += len(v)
            print("INF: describing %d actions(s)" % nSumActions )

        if not self.bUsePickle:
            f = open(self.strSaveFilename,"wt") # 16s  (for a file of 333M)
            #~ f = gzip.open(self.strSaveFilename,"wt") # >  70s
            ret = json.dump((self.mem),f,indent=2, ensure_ascii=False)
        else:
            f = open(self.strSaveFilename,"wb")
            pickle.dump(self.mem,f)
        f.close()
        
    def load(self):
        print("INF: loading from '%s'" % self.strSaveFilename)
        try:
            if not self.bUsePickle or 0:
                f = open(self.strSaveFilename,"rt")
                dictlist = json.load(f)
                self.mem = dictlist
            else:
                f = open(self.strSaveFilename,"rb")
                self.mem = pickle.load(f)
            f.close()
        except FileNotFoundError: pass
        
        print("INF: loaded %d situation(s)" % len(self.mem) )
        if 1:
            nSumActions = 0
            for k,v in self.mem.items():
                nSumActions += len(v)
            print("INF: describing %d actions(s)" % nSumActions )
        if 0:
            print("DBG: load: compressing keys and actions...")
            # compress keys
            dup = copy.deepcopy(self.mem)
            self.mem = {}
            for k,v in dup.items():
                kcomp = k.replace('0','').replace(' ', '')
                # compress actions
                vcomp = {}
                for kk,vv in v.items():
                    kkcomp = kk.replace('(', '').replace(')', '').replace(' ', '')
                    vcomp[kkcomp] = vv
                #~ print("action: %s => %s" % (v,vcomp))
                self.mem[kcomp] = vcomp
        if 0:
            print("INF: loaded %d situation(s) (after recomp)" % len(self.mem) )
            nSumActions = 0
            for k,v in self.mem.items():
                nSumActions += len(v)
            print("INF: describing %d actions(s) (after recomp)" % nSumActions )
        
    @staticmethod
    def _getKeySituation(world, num_player):
        o =  "%s__%s" % (str(world),num_player)
        o = o.replace('0', '').replace(' ', '') # 'compress' data
        return o

    @staticmethod
    def _getKeyAction(action):
        o = "%s" % (str(action))
        o = o.replace('(', '').replace(')', '').replace(' ', '')
        return o
        
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
        bVerbose = 1
        bVerbose = 0
        k = self._getKeySituation(world, num_player)
        try:
            listKnown = self.mem[k]
        except KeyError as err:
            print("DBG: getAction: unknown situation => random (key:%s)" % str(err))
            return possible_action[random.randint(0,len(possible_action)-1)]
        
        if bVerbose: print("DBG: getAction: listKnown: %s" % str(listKnown))            
        #~ listKnownSortedKeys = sorted(listKnown,key = lambda x: x[1])
        listKnownSortedKeys = [x for _,x in sorted(zip(listKnown.values(),listKnown.keys()),reverse=True)]
        if bVerbose: print("DBG: getAction: listKnown sorted keys: %s" % str(listKnownSortedKeys))
        rSumPositive = 0
        allPositiveGain = []
        for i,k in enumerate(listKnownSortedKeys):
            potential_gain = listKnown[k]
            if potential_gain<=0:
                break
            allPositiveGain.append(potential_gain)
        if bVerbose: print("DBG: getAction: allPositiveGain: %s" % str(allPositiveGain))
        if len(allPositiveGain) > 0:
            i = chooseWeighted(allPositiveGain)
            pos = listKnownSortedKeys[i]
            pos = posStringToPos(pos)
            print("DBG: getAction(1): pos: %s" % str(pos) )
            return pos
            
        # soit il y en a un dans la liste qui n'a jamais ete essay�, soit on prend le moins mauvais (randomly)
        listNotTested = []
        for act in possible_action:
            if self._getKeyAction(act) not in listKnown:
                listNotTested.append(act[:])
        if bVerbose: print("DBG: getAction: listNotTested: %s" % str(listNotTested))
        if len(listNotTested) > 0:
            return listNotTested[random.randint(0,len(listNotTested)-1)]
            
        # choose among the negative one
        listKnownPositived = [1+v for v in listKnown.values()]
        if bVerbose: print("DBG: getAction: listKnownPositived: %s" % str(listKnownPositived))
        if bVerbose: print("DBG: getAction: listKnown: %s" % listKnown )
        i = chooseWeighted(listKnownPositived)
        pos = list(listKnown.keys())[i]
        if bVerbose: print("DBG: getAction (2a): pos as str: %s" % pos )
        pos = posStringToPos(pos)
        if bVerbose: print("DBG: getAction (2b): pos as tuple: %s" % str(pos) )
        return pos
    # getAction - end
                
        
    def updateStats(self,num_winner,num_player_ai):
        """
        at the end of a game, take some decisions about 
        what could have been made better and memorize them
        - num_winner: player who wins this game
        """
        bVerbose = 1
        bVerbose = 0
        if bVerbose: print("DBG: updateStats: current actions: %s" % str(self.currentActions))
        if bVerbose: print("DBG: updateStats: prev mem: %s" % str(self.mem))
            
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
        
        if bVerbose: print("DBG: updateStats: new mem: %s" % str(self.mem))
        self.currentActions = []
        if self.bAutosave: self.save()
    # updateStats - end
# class AiCpu - end
