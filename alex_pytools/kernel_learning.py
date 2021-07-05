# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# learn features and create svm like kernel (but faster and idiot way)
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# scp -pw ******** C:\work\Dev\git\protolab_group\abcdk\sdk\abcdk\kernel_learning.py amazel@10.0.161.8:/home/amazel/dev/git/protolab_group/face_tools

import math
import os
import shutil
import time

import numpy as np


def assert_equal( x, y ):
    if x != y:
        print( "%s != %s" % ( str(x), str(y) ) )
        assert(0)

def assert_equal_near( x, y, rThreshold = 0.25 ):
    if abs(x-y) > rThreshold:
        print( "%s != %s" % ( str(x), str(y) ) )
        assert(0)        

        

class Kernel:
    """
    a representation of a kernel of a featured class
    all vectors will be numpy arrays
    """
    def __init__( self, nNumClass = -1 ):
        self.reset()
        self.nNumClass = nNumClass
        
    def reset( self ):
        self.nNumClass = -1 # which class does it represent ?
        self.vAvg = []
        self.nAvgNbr = 0 # nbr of vector used to compute avg
        self.rSize = 0. # approximation of the kernel size - actually: biggest difference learnt
        self.allNew = [] # store all new vectors (before stacking them to vAvg)
        
    def serialize( self ):
        """
        return a string defining the complete object
        """
        s = ""
        s += "["
        s += repr(self.nNumClass) + ','
        s += repr(self.vAvg.tolist()) + ','
        s += repr(self.nAvgNbr) + ','
        s += repr(self.rSize) + ','
        s += repr([x.tolist() for x in self.allNew])
        s += "]"
        return s

    def unserialize( self, s ):
        """
        recreate the object from a string
        """
        self.reset()
        #~ print("eval s: %s " % str(s) )
        datas = eval(s)
        self.nNumClass = datas[0]
        self.vAvg = np.array(datas[1])
        self.nAvgNbr = datas[2]
        self.rSize = datas[3]
        self.allNew = datas[4]
        #~ print("self.allNew: %s" % str(self.allNew) )
        for i in range(len(self.allNew)):
            self.allNew[i] = np.array(self.allNew[i])
        
    def getClassNum( self ):
        return self.nNumClass
        
    def getCenter( self ):
        """
        return the center of the kernel
        """
        return self.vAvg
        
    def getAverageNumber( self ):
        """
        return the center of the kernel
        """
        return self.nAvgNbr
        
    def getNbrTotalSamples( self ):
        """
        return all the sample stored by this kernel (in average + in new)
        """
        return self.nAvgNbr+len(self.allNew)
        
    def getSize( self ):
        """
        return the center of the kernel
        """
        return self.rSize
        
    def add( self, v, nThresholdAutoUpdate ):
        self.allNew.append(np.array(v))
        if self.nAvgNbr != 0:
            rDist = self.dist(v)    
            if rDist > self.rSize:
                self.rSize = rDist
        if len(self.allNew) > nThresholdAutoUpdate or self.nAvgNbr == 0:
            self.update()
        
    def dist( self, v ):        
        return np.linalg.norm(self.vAvg - v) # axis=0 only for python3 ?
    
    def update( self ):
        if len(self.allNew) < 1:
            # nothing to do!
            return
        vMean = np.mean( self.allNew, axis=0)
        nNewNbr = self.nAvgNbr + len(self.allNew)
        #~ print("vMean: %s" % vMean )
        #~ print("self.vAvg: %s" % self.vAvg )
        if self.nAvgNbr == 0:
            newAvg = vMean
        else:
            newAvg = (self.vAvg * self.nAvgNbr + vMean * len(self.allNew))/nNewNbr
            
        if 0:
            print("DBG: Kernel.update(%d): isnan: %s (%d) => %s (%d)" % (self.nNumClass,self.vAvg, self.nAvgNbr,newAvg, nNewNbr) )
            
            print("DBG: Kernel.update: isnan: self.vAvg: %s" % str(self.vAvg ) )
            print("DBG: Kernel.update: isnan: self.nAvgNbr: %s" % str(self.nAvgNbr ) )
            print("DBG: Kernel.update: isnan: vMean: %s" % str(vMean ) )
            print("DBG: Kernel.update: isnan: nNewNbr: %s" % str(nNewNbr ) )
            assert( not math.isnan(newAvg[0]) )
            assert( not math.isnan(newAvg[1]) )
            assert( nNewNbr != 0 )
        
        self.vAvg = newAvg
        self.nAvgNbr = nNewNbr
        self.allNew = []
        
        
    def repr( self ):
        strOut = ""
        return strOut
        
# class Kernel - end
        
        
class KernelManager:
    """
    handle all kernel for many classes
    """
    
    def __init__( self, nThresholdAutoUpdate = 10 ):
        self.nThresholdAutoUpdate = nThresholdAutoUpdate
        self.reset()
        
    def setThreshold( self, rThresholdTwoKernel, rThresholdTwoClasses, rThresholdTooCloseToCreateNew ):
        assert rThresholdTwoKernel < rThresholdTwoClasses
        assert rThresholdTwoClasses <= rThresholdTooCloseToCreateNew
        self.rThresholdTwoKernel = rThresholdTwoKernel
        self.rThresholdTwoClasses = rThresholdTwoClasses
        self.rThresholdTooCloseToCreateNew = rThresholdTooCloseToCreateNew
        
    def reset( self ):
        """
        reset doesn't reset any thresholds !!!
        """
        self.kernels = [] # list of kernels in random order
        self.dictClass = dict() # for each class a list of kernel
        self.nNextClassNum = 0
        
    def serialize( self ):
        """
        return a string defining the complete object
        """
        s = ""
        s += "["
        for k in self.kernels:
            s += '"' + k.serialize() + '"' + "," # let's keep it enclosed in a string, so it will be unserialize as it is
        s += "]\n"
        s += repr(self.dictClass) + "\n"
        s += repr(self.nNextClassNum)
        return s

    def unserialize( self, s ):
        """
        recreate the object from a string
        """
        self.reset()
        #~ print("s: %s" % str(s))
        lines = s.split("\n")
        #~ print("lines: %s" % str(lines))
        kernels = eval(lines[0])
        for ks in kernels:
            k = Kernel()
            k.unserialize(ks)
            self.kernels.append(k)
        self.dictClass = eval(lines[1])
        self.nNextClassNum = eval(lines[2])
        
        
    def save( self, filename ):
        timeBegin = time.time()
        try:
            buf = self.serialize()
            file = open(filename, "wt")
            file.write(buf)
            file.close()
            print( "INF: KernelManager: %d kernel(s) defining %d classe(s) - saved in %5.2fs" % (len(self.kernels), len(self.dictClass), time.time()-timeBegin) )
        except: return False
        return True
        
    def load( self, filename ):
        timeBegin = time.time()
        try:
            file = open(filename, "rt")
            buf = file.read()
            self.unserialize(buf)
            file.close()
            print( "INF: KernelManager: %d kernel(s) defining %d classe(s) - loaded, in %5.2fs" % (len(self.kernels), len(self.dictClass), time.time()-timeBegin) )
        except: return False
        return True        
        
    def _addKernel( self, nClassNum ):
        """
        add a kernel, return its index
        """
        self.kernels.append(Kernel(nClassNum))
        nNewIndex = len(self.kernels)-1
        if nClassNum not in self.dictClass.keys():
            self.dictClass[nClassNum] = []        
        self.dictClass[nClassNum].append(nNewIndex)
        return nNewIndex
        
    def add( self, v, nNumClass = -1, rConfidence = 1. ):
        """
        rConfidence: a value in [0.,1.] expressing the confidence in the datas. A bad confidence data, shouldn't be learned too much
        return status, class num
            5: value returned but nothing learned
            2: learn (it's a new id !!!)
            1: learn (new kernels)
            0: learn (updated)
            -1: when nNumClass is specified: this vector is too close of an existing one for another kernel
            -1: when nNumClass is not specified: this vector is too close of an existing one so skipping it
            -2: not sure, will learn, but the class is not that sure yet
            -3: not sure, will not learn, reference is weak
            -4: not sure: two different classnum could match
            -10: unknown error
        """    
        bSure = rConfidence > 0.4
        
        v = np.array(v)
        rDistMin = 30000
        iMin = -1
        rDistMin2 = 30000 # the 2nd nearest # can be before the 1st or later
        iMin2 = -1
        
        for i ,k in enumerate(self.kernels):
            rDist = k.dist(v)            
            #~ print("i: %d(class:%d), rDist: %5.2f" % (i,self.kernels[i].getClassNum(),rDist) )            
            if rDist < rDistMin:
                if rDistMin < rDistMin2:
                    rDistMin2 = rDistMin
                    iMin2 = iMin
                rDistMin = rDist
                iMin = i
            elif rDist < rDistMin2:
                    rDistMin2 = rDist
                    iMin2 = i
                    
        # NB: iMin can only be at -1 on the first add (really?)
        
        if nNumClass != -1:
            # force the update for a given class
            
            if rDistMin < self.rThresholdTwoClasses and iMin != -1 and self.kernels[iMin].getClassNum() != nNumClass:
                # this vector looks like another class, won't add it
                print("DBG: Kernel.add: rDistMin: %5.2f, iMin: %d(%d), rDistMin2: %5.2f, iMin2: %d(%d), nNumClass: %d, self.kernels[iMin]: %d => returning -1: this vector is too close of an existing one for another kernel" % (rDistMin, iMin, self.kernels[iMin].getClassNum(), rDistMin2, iMin2, self.kernels[iMin2].getClassNum(), nNumClass, self.kernels[iMin].getClassNum() ) )
                return -1, -1
                
            # all the other case are ok:
            # rDistMin >  rThresholdTwoClasses > rThresholdTwoKernel => a new one will be added
            # or getClassNum() == nNumClass, then depending of the case => new kernel or reusing
            
        nSelectedKernel = iMin
        nSizeIMin = 0
        if iMin !=-1:
            nSizeIMin = self.kernels[iMin].getNbrTotalSamples()
        nSizeIMin2 = 0
        if iMin2 !=-1:
            nSizeIMin2 = self.kernels[iMin2].getNbrTotalSamples()
            
        print("DBG: Kernel.add: rDistMin: %5.2f, iMin: %d(size:%d) (rDistMin2: %5.2f, iMin2: %d(size:%d))" % (rDistMin,iMin,nSizeIMin,rDistMin2,iMin2,nSizeIMin2) )
        if  (
                (rDistMin2 < self.rThresholdTwoClasses and nSizeIMin2 > 4 and nSizeIMin < 3) 
                or
                (rDistMin2 < 0.35 and nSizeIMin2 > 1 and nSizeIMin < 2) # if second threshold is very close, then select it # TODO parametrised threshold!
            ):
        
            print("WRN: Kernel.add: promoting %d (size:%d) instead of %d (size:%d) because the last one seems weak" % (iMin2,  nSizeIMin2, iMin, nSizeIMin) )
            iMin = iMin2
            rDistMin = rDistMin2
            nSelectedKernel = iMin2
            
        nStatus = -10 # unknown error
        
        #~ if rDistMin > 0.40 and rDistMin < self.rThresholdTwoClasses and rDistMin2 < self.rThresholdTwoClasses and self.kernels[iMin2].getClassNum() != self.kernels[iMin].getClassNum():
            #~ # case borderline match and second choice is of a different classes
            #~ return -4,-1
            
        # remove hesitation with one young class
        if rDistMin > 0.45 and rDistMin < 0.50 and nSizeIMin < 3: # TODO parametrised threshold!
            return -4, -1
            
            
        #~ if not bSure and nSelectedKernel != -1:
            #~ return 5, self.kernels[nSelectedKernel].getClassNum()
        
        if rDistMin < self.rThresholdTwoKernel: # if an error is raised here: you need to call first setTreshold to define your way to learn
            nStatus = 0
        elif rDistMin < self.rThresholdTwoClasses:
            # create a new kernel related to the found one
            nStatus = 1
            if  self.kernels[iMin].getNbrTotalSamples() > 1:
                nSelectedKernel = self._addKernel( self.kernels[iMin].getClassNum() )
            else:
                nSelectedKernel = iMin
                print("WRN: Kernel.add: not really creating a new kernel associated to the original, as the original seems weak..." )
                nStatus = -3
        else:
            if rDistMin < self.rThresholdTooCloseToCreateNew:
                return -1,-1
            # create a new kernel
            # first case (empty kernels) goes here also
            nStatus = 2
            if rDistMin < 0.60: # TODO parametrised threshold!
                # it's a new guy close to an existing one, so we're not that sure!
                nStatus = -2
            if nNumClass == -1:
                nSelectedKernel = self._addKernel( self.nNextClassNum )
                self.nNextClassNum += 1 # TODO: thread safe this
            else:
                nSelectedKernel = self._addKernel( nNumClass )
                self.nNextClassNum = nNumClass+1 # TODO: thread safe this                
        self.kernels[nSelectedKernel].add(v, self.nThresholdAutoUpdate)
        print("DBG: Kernel.add(%d): selected k: %d, rDistMin: %5.2f, iMin: %d(class:%d)(rDistMin2: %5.2f, iMin2: %d(class:%d))\n" % (self.kernels[nSelectedKernel].getClassNum(), nSelectedKernel, rDistMin,iMin,self.kernels[iMin].getClassNum(),rDistMin2,iMin2,self.kernels[iMin2].getClassNum()) )
            
        return nStatus, self.kernels[nSelectedKernel].getClassNum()
        
    def update(self):
        for i ,k in enumerate(self.kernels):
            self.kernels[i].update()
            
    def killInactive(self):
        """
        WARNING: after that, all kernel index will probably change !
        """
        nNumKernel = 0
        while nNumKernel < len(self.kernels):
            if self.kernels[nNumKernel].getNbrTotalSamples() < 2:
                # a kernel representing one or two vectors
                print("DBG: Kernel.killInactive: removing kernel %d, (class:%d)" % (nNumKernel, self.kernels[nNumKernel].getClassNum()) )
                # kill inactive: small and old (a small one could have been added or updated recently) # TODO: check old !
                if len(self.dictClass[self.kernels[nNumKernel].getClassNum()]) < 2:
                    # no more class
                    del self.dictClass[self.kernels[nNumKernel].getClassNum()]
                else:                
                    idx = self.dictClass[self.kernels[nNumKernel].getClassNum()].index(nNumKernel)
                    del self.dictClass[self.kernels[nNumKernel].getClassNum()][idx]
                    
                del self.kernels[nNumKernel]
                # update all kernel index higher than nNumKernel in dictClass !!! by decrement 1
                for k,v in self.dictClass.items():
                    for ki,kn in enumerate(v):
                        if kn > nNumKernel:
                            v[ki] = kn-1
                continue
            self.kernels[nNumKernel].update()
            nNumKernel += 1            
            
            
    def getNbrClass(self):
        return len(self.dictClass)
        
    def getClass(self, v):
        """
        find wich class is nearest v
        return (class number, dist) or -1 if none
        """
        v = np.array(v)
        rDistMin = 30000
        iMin = -1
        for i ,k in enumerate(self.kernels):
            rDist = k.dist(v)
            if rDist < rDistMin:
                rDistMin = rDist
                iMin = i
        if iMin == -1:
            return -1,-1
        return self.kernels[iMin].getClassNum(), rDistMin
        
    def getStatus( self ):
        strOut = ""
        strOut += "nbr kernel: %d\n" % len(self.kernels)
        strOut += "nbr class: %d\n" % len(self.dictClass)
        for k,v in self.dictClass.items():
            nTotal = 0
            strOutK = ""
            for nk, ik in enumerate(v):
                nb = self.kernels[ik].getNbrTotalSamples()
                strOutK += " - nbr sample in kernel %d: %d\n" % (nk,nb)
                nTotal += nb
            strOut += "class: %3d, nbr kernel: %3d, total sample: %5d\n" % (k,len(v),nTotal)
            strOut += strOutK
        strOut += "dictClass: %s\n" % str(self.dictClass)

        return strOut
        
    def printStatus( self ):
        s = self.getStatus()
        print( s  )
            
    def render(self):
        """
        render only on 2D the two first element in the feature
        """
        import cv2
        w = 800
        h = 600
        w2 = int(w/2)
        h2 = int(h/2)
        rZoom = 10
        if 1:
            # autozoom
            rMinX = 100
            rMinY = 100
            rMaxX = -100
            rMaxY = -100            
            for k in self.kernels:
                c = k.getCenter()
                if c[0] < rMinX:
                    rMinX = c[0]
                if c[0] > rMaxX:
                    rMaxX = c[0]
                if c[1] < rMinY:
                    rMinY = c[1]
                if c[1] > rMaxY:
                    rMaxY = c[1]
            rZoom = min(w2/rMaxX,h2/rMaxY)
            print( "DBG:kernel_learning.render: rZoom: %5.2f" % (rZoom) )
                    
        im = np.zeros( (h,w,3), np.uint8 )
        im[:] = (255,255,255)
        black = (0,0,0)
        grey = (180,180,180)
        cv2.line(im, (0,h2), (w,h2), black, 1 )
        cv2.line(im, (w2,0), (w2,h), black, 1 )
        for k in self.kernels:
            c = k.getCenter()
            x = int(w2+c[0]*rZoom)
            y = int(h2-c[1]*rZoom)
            cv2.circle(im, ( x, y ), 1, black,-1 )
            rSize = k.getSize()
            cv2.circle(im, ( x, y ), int(rSize*rZoom), grey )            
            txt = str(k.getClassNum() )
            fontFace = 0
            fontScale = 0.4
            thickness = 1
            cv2.putText( im, txt, (x, y-10 ), fontFace, fontScale, black, thickness )
            if 1:
                # render all 
                for k2 in k.allNew:
                    x = int(w2+k2[0]*rZoom)
                    y = int(h2-k2[1]*rZoom)
                    cv2.circle(im, ( x, y ), 0, black )
                    
        strWin = "kernel"
        cv2.imshow( strWin, im )
        cv2.moveWindow( strWin, 0, 0 )
        cv2.waitKey(0)        
        
# class KernelManager - end
    
kernelManager = KernelManager()
        
        
def autoTest():
    import random    
    km = KernelManager()
    km.setThreshold( 2, 10,11 )
    km.add([1,1],0)
    km.add([1,1])
    km.add([1,2])
    km.add([0,1])
    km.add([15,1])
    km.add([15,2])
    km.add([15,2.1])
    
    for i in range(30):
        km.add([random.random(),random.random()+1])
    
    for i in range(30):
        km.add([random.random(),random.random()])
        
    for i in range(300): #was 300
        km.add([20+random.random(),20+random.random()*5] )
    
    km.printStatus()

    if 1:
        print( "load/save test" )

        km.printStatus()    
        nbrKernelsPrev = len(km.kernels)
        assert( not km.save("/caca/pipi") )# doesn't exists
        assert( km.save("/tmp/k.dat") )
        km.reset()
        km.printStatus()
        assert_equal(len(km.kernels), 0 )    
        assert( not km.load("/caca/toto") )
        assert( km.load("/tmp/k.dat") )
        km.printStatus()
        assert_equal(len(km.kernels), nbrKernelsPrev )

    km.render()        
    
    km.update()
    
    km.render()
    
    retVal = km.getClass([1,1.1])
    print("retVal: %s" % str(retVal) )
    assert_equal(retVal[0], 0) # retVal: (0, 0.49954919925540447)
    assert_equal_near(retVal[1], 0.5)
    
    retVal = km.getClass([15,1.1])
    print("retVal: %s" % str(retVal) )
    assert_equal(retVal[0], 1) # retVal: (1, 0.59999999999999987)
    assert_equal_near(retVal[1], 0.6)

    retVal = km.getClass([20,21])
    print("retVal: %s" % str(retVal) )
    assert_equal(retVal[0], 2) # retVal: (2, 0.63786069753148411)
    assert_equal_near(retVal[1], 0.60, 0.15)
    
    km.render()
    
    km.printStatus()
    
    # killing
    print( "INF: test killing inactive" )
    retVal = km.add([1000,1000])
    assert_equal_near(retVal[1], 3)
    retVal = km.add([2000,2000],10)
    assert_equal_near(retVal[1], 10)
    retVal = km.add([3000,3000])
    assert_equal_near(retVal[1], 11)
    
    
    km.render()
    km.printStatus()
    
    assert_equal( km.getNbrClass(), 6 )
    km. killInactive()    
    km.printStatus()
    assert_equal( km.getNbrClass(), 3 )
    
if __name__ == "__main__":
        autoTest()
