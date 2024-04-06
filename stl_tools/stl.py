# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Stereolithography Tools: load, split and merge
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""
When invoked from command line, two functionnalities are offered:

1) quick viewer
scriptname <stl_file>: will render the file on screen
eg: python stl.py toto.stl

2) splitter
scriptname <stl_file> <start of filename>: will split all independant object in separate files
eg: python stl.py toto.stl /tmp/elem => will write object in many /tmp/elem__*__*.stl
"""


import struct
import sys
import time

def print_grey(s):
    """
    print in grey (diminued)
    """
    try:
        from colorama import Fore, Back, Style, init
        init()
        print( Fore.BLACK + Style.BRIGHT + s ) # bright blacks looks like grey
    except BaseException as err:
        # print( "DBG: err: %s" % err) # to debug this method
        print( s ) # no colorama => no color, it's ok...
        
def prind(s):
    """
    print debug info
    """
    print_grey(s)
    
def print_progress( nCurrent, nTotal ):
    """
    print a progression
    (5800 print takes around 2 seconds on my tablet - 0.34ms per call)
    """
    s = "%d/%d" % (nCurrent, nTotal)
    print( s + '\r' ),
        
def list_to_tuple( l ):
    t = tuple()
    for i in range(len(l)):
        t = t + (l[i],)
    return t
    
def isSamePoint(v1, v2, rEqualThreshold ):
        for i in range(3):
            rDiff = abs(v1[i] - v2[i])
            if rDiff > rEqualThreshold:
                return False
        return True

class StlTriangle:
    """
    a simple triangle
,     """
    def __init__( self, p1 = (0.,0.,0.), p2 = (0.,0.,0.), p3 = (0.,0.,0.) ):
        self.nv = (0., 0., 0. ) # the normal ?
        #~ self.v = [ (0., 0., 0. ), (0., 0., 0. ), (0., 0., 0. ) ]
        self.v = [ p1,p2,p3 ]
        self.attr = 0
        
    def __str__( self ):
        strOut = ""
        strOut += "    nv: %s\n" % str( self.nv )
        strOut += "    v1: %s\n" % str( self.v[0] )
        strOut += "    v2: %s\n" % str( self.v[1] )
        strOut += "    v3: %s\n" % str( self.v[2] )
        strOut += "    attr: %s\n" % str( self.attr )
        return strOut
        
    def hasCommonVertexWithAnotherTriangle( self, rhs, rEqualThreshold = 0.01 ):
        for i in range(3):
            for j in range(3):
                if isSamePoint(self.v[i], rhs.v[j], rEqualThreshold ):
                    return True
                
        return False
        
    def hasCommonVertex( self, vertex, rEqualThreshold = 0.01 ):
        for i in range(3):
            if isSamePoint(self.v[i], vertex, rEqualThreshold ):
                return True
                
        return False
        
class StlObject:
    """
    a list of triangles
    """
    def __init__( self ):
        self.aTriangles = []
        
    def hasCommonVertex( self, vertex ):
        """
        Does this object has a vertex in one of its triangles vertexes ?
        """
        for t in self.aTriangles:
            if t.hasCommonVertex( vertex ):
                return True
        return False
        
    def hasCommonVertexWithAnotherTriangle( self, tri, rEqualThreshold = 0.01 ):
        for t in self.aTriangles:
            if t.hasCommonVertexWithAnotherTriangle( tri ):
                return True
        return False
        
        
    def split( self ):
        """
        return a collection of objects from one object.
        Objects are splitted by independant vertex: if one vertex has no connection with others, it's another object
        """
        timeBegin = time.time()
        prind( "DBG: Stl.split: part1..." )
        splittedObjectsList = []
        for i in range(len(self.aTriangles) ):
            print_progress( i, len(self.aTriangles) )
            newT = self.aTriangles[i]
            # find if this object belong to one of the newly created object
            for numObject in range( len(splittedObjectsList) ):
                if splittedObjectsList[numObject].hasCommonVertexWithAnotherTriangle( newT ):
                    splittedObjectsList[numObject].aTriangles.append( newT )
                    break
            else:
                # this triangle doesn't belong to a previous created object
                splittedObjectsList.append( StlObject() )
                splittedObjectsList[-1].aTriangles.append(newT)
        prind("DBG: duration: %5.2fs" % (time.time() - timeBegin) )
                
        # if triangle weren't described in a sequential order, we can have produce too much objects
        # merging
        timeBegin2 = time.time()
        prind( "DBG: Stl.split: part2..." )
        numObject1 = 0
        while numObject1 < len(splittedObjectsList):
            #if numObject1 > 3 and (numObject1%4)==0: prind( "DBG: split: %d/%d" % (numObject1,len(splittedObjectsList)) ) 
            
            numObject2 = numObject1 + 1
            while numObject2 < len(splittedObjectsList):
                print_progress( numObject2, len(splittedObjectsList) )
                for t in splittedObjectsList[numObject2].aTriangles:
                     if splittedObjectsList[numObject1].hasCommonVertexWithAnotherTriangle( t ):
                        #  numObject1 and numObject2 are same object
                        splittedObjectsList[numObject1].aTriangles.extend(splittedObjectsList[numObject2].aTriangles)
                        del splittedObjectsList[numObject2]
                        break
                else:
                    numObject2 += 1
            numObject1 += 1
        prind("DBG: duration: %5.2fs (total: %5.2fs)" % (time.time() - timeBegin2,time.time() - timeBegin) )

        return splittedObjectsList
        
    def saveToStl( self, strFilename ):
        file = open( strFilename, "wb")
        if sys.version_info[0] >= 3:
            buf = b""
        else:
            buf = ""
            
        buf += struct.pack( "80B", *((0,)*80) )
        buf += struct.pack( "I", len(self.aTriangles) )
        
        for t in self.aTriangles:
            buf += struct.pack( "3f", *t.nv)
            for i in range(3):
                buf += struct.pack( "3f", *t.v[i])
            buf += struct.pack( "H", t.attr)
            
        file.write(buf)
        file.close()
        
    def addTriangle( self, p1,p2,p3):
        self.aTriangles.append(StlTriangle(p1,p2,p3))
# class StlObject - end
                        

class Stl:
    """
    Manipulate stl file and array of object of list of triangles
    """
    def __init__( self ):
        self.reset()
        
    def reset( self ):
        self.aObjects = [] # a list of StlObject
        
    def load( self, strFilename ):
        """
        return True if ok
        """
        """
        Stl bin format:
            UINT8[80] - Header
            UINT32 - Number of triangles


            foreach triangle
                REAL32[3] - Normal vector
                REAL32[3] - Vertex 1
                REAL32[3] - Vertex 2
                REAL32[3] - Vertex 3
                UINT16 - Attribute byte count
            end
        """
        print( "INF: Stl.load: loading '%s'\n" % strFilename )
        file = open( strFilename, "rb" )
        buf = file.read()
        file.close()
        prind( "DBG: Stl.load: buf length: %d" % len(buf) )
        
        self.reset()
        
        nOffset = 0
        
        strHeader = struct.unpack_from( "80B", buf , nOffset ); nOffset += 80
        #~ prind( "DBG: strHeader: %s" % str(strHeader) )
        
        nbrTriangles = struct.unpack_from( "I", buf, nOffset )[0]; nOffset += 4
        prind( "DBG: Stl.load: nbrTriangles: %s" % str(nbrTriangles) )
        
        self.aObjects.append(StlObject())
        
        for i in range( nbrTriangles ):
            nv = struct.unpack_from( "3f", buf, nOffset ); nOffset += 4*3
            v1 = struct.unpack_from( "3f", buf, nOffset ); nOffset += 4*3
            v2 = struct.unpack_from( "3f", buf, nOffset ); nOffset += 4*3
            v3 = struct.unpack_from( "3f", buf, nOffset ); nOffset += 4*3
            attr = struct.unpack_from( "H", buf, nOffset )[0]; nOffset += 2
            
            if 0:
                prind( "DBG: nv: %s" % str(nv) )
                prind( "DBG: v1: %s" % str(v1) )
                prind( "DBG: v2: %s" % str(v2) )
                prind( "DBG: v3: %s" % str(v3) )
                prind( "DBG: attr: %s" % str(attr) )
            
            attr = i # to debug, add the original triangle index to attr
            
            # add this triangles to the StlObjects
            self.aObjects[-1].aTriangles.append( StlTriangle() )
            self.aObjects[-1].aTriangles[-1].nv = nv
            self.aObjects[-1].aTriangles[-1].v[0] = list_to_tuple(v1)
            self.aObjects[-1].aTriangles[-1].v[1] = list_to_tuple(v2)
            self.aObjects[-1].aTriangles[-1].v[2] = list_to_tuple(v3)
            self.aObjects[-1].aTriangles[-1].attr = attr
            
        # triangles - end
        #~ prind( "DBG: self (1): %s" % str(self) )
        
        prind( "DBG: Stl.load: nbr object before split: %d" % len(self.aObjects) )
        
        self.aObjects = self.aObjects[0].split()
        
        prind( "DBG: Stl.load: nbr object after split: %d" % len(self.aObjects) )
        
        #~ prind( "DBG: self (2): %s" % str(self) )
        
    def __str__( self ):
        strOut = ""
        strOut += "Nbr Objects: %d\n\n" % len( self.aObjects )
        for i in range( len(self.aObjects) ):
            strOut += "  Nbr Triangles: %d\n" % len( self.aObjects[i].aTriangles )
            for j in range( min(300, len(self.aObjects[i].aTriangles)) ):
                strOut += "  Triangle %d:\n%s\n" % (j, str(self.aObjects[i].aTriangles[j]) )
        return strOut
        
    def render( self ):
        prind( "DBG: Stl.render: starting..." )
        try:
            import numpy as np
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            from matplotlib import cm
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            x = []
            y = []
            z = []
            colors=[]
            if 0:
                for nNumObject in range(len(self.aObjects)):
                    for nNumTriangle in range(len(self.aObjects[nNumObject].aTriangles)):
                        for j in range(3):
                            x.append(self.aObjects[nNumObject].aTriangles[nNumTriangle].v[j][0])
                            y.append(self.aObjects[nNumObject].aTriangles[nNumTriangle].v[j][1])
                            z.append(self.aObjects[nNumObject].aTriangles[nNumTriangle].v[j][2])
                            colors.append(['y','y','y'])
                        #~ if nNumTriangle > 2:
                            #~ break
                print(x)
                print(y)
                print(z)
                print(colors)
                x = np.array(x)
                y = np.array(y)
                z = np.array(z)
                colors = np.array(colors)
                print(colors.shape)
                #~ ax.plot_surface(x, y, z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
                ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True) # , color=colors
            else:
                colors = ['r','b','g','y'] 
                for nNumObject in range(len(self.aObjects)):
                    for nNumTriangle in range(len(self.aObjects[nNumObject].aTriangles)):
                        x = []
                        y = []
                        z = []
                        for j in range(3):
                            x.append(self.aObjects[nNumObject].aTriangles[nNumTriangle].v[j][0]+j*0.0001) # need to have always differet x and y (we're rendering shape in a data visualisator...)
                            y.append(self.aObjects[nNumObject].aTriangles[nNumTriangle].v[j][1]+j*0.0001)
                            z.append(self.aObjects[nNumObject].aTriangles[nNumTriangle].v[j][2])
                        x = np.array(x)
                        y = np.array(y)
                        z = np.array(z)
                        #~ print x
                        #~ print y
                        #~ print z
                        ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True, color=colors[nNumObject%len(colors)])                    

            plt.show()
        except BaseException as err:
            print("ERR: Stl.render: error: %s" % str(err) ) # once in plot_trisurf:  Error in qhull Delaunay triangulation calculation: singular input data (exitcode=2); use python verbose option (-v) to see original qhull error. 
        
        
    def getNbrObjects( self ):
        return len(self.aObjects)
        
    def saveByObject( self, strFilenameStart, bRenderThem ):
        """
        save each object in separate file named <strFilenameStart>__object_index__triangles_number.stl
        """
        for i in range(len(self.aObjects)):
            nNbrTriangles = len(self.aObjects[i].aTriangles)
            strFilename = strFilenameStart + ("__%03d" % i) + ("__%04d" % nNbrTriangles) + ".stl"
            print( "INF: saving object '%d' to '%s' (%d triangles)" % (i, strFilename, nNbrTriangles) )
            self.aObjects[i].saveToStl(strFilename)
            if bRenderThem:
                viewStl( strFilename )
        
# class Stl - end

def viewStl( strFilename ):
    stl = Stl()
    stl.load(strFilename)
    stl.render()
    
def splitStl( strFilename, strDstFilenameStart, bRenderEachSavedObject = False ):
    stl = Stl()
    stl.load(strFilename)
    stl.saveByObject( strDstFilenameStart, bRenderThem = bRenderEachSavedObject ) 
    
def autoTest():
    stl = Stl()
    stl.load("cube.stl")
    nNbrObjects = stl.getNbrObjects()
    print( "nNbrObjects: %d" % nNbrObjects )
    #~ stl.render()
    assert( nNbrObjects == 1 )

    stl.load("test_slices.stl")
    nNbrObjects = stl.getNbrObjects()
    print( "nNbrObjects: %d" % nNbrObjects )
    #~ stl.render()
    assert( nNbrObjects == 2 )
    stl.saveByObject( "/tmp/elem_" )        
    
    
if( __name__ == "__main__" ):
    #~ autoTest();
    if len(sys.argv)==2:
        viewStl( sys.argv[1])
    if len(sys.argv)==3:
        splitStl( sys.argv[1], sys.argv[2] )
        
    #splitStl( "C:/Users/amazel/Downloads/PepperBackSmall(5).stl", "/tmp/t" )
#~ splitStl( "C:/Users/amazel/Downloads/Meuble SDB.stl", "/tmp/sdb" )    
#~ splitStl( "Meuble SDB.stl", "/tmp/sdb" )    
