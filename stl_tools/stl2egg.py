# from http://codepad.org/dlG9cKKQ
# by Riccardo126 on 2 oct 2020

import sys
#Using struct for Bin file reading
import struct

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3D, Vec3D, VBase4
from panda3d.egg import EggData, EggPolygon, EggVertexPool, EggVertex

class AppShow(ShowBase):
    def __init__(self, filename):
        ShowBase.__init__(self)
        # Load the environment model.
        self.model = self.loader.loadModel(filename)
        # Reparent the model to render.
        self.model.reparentTo(self.render)
        self.model.setRenderModeWireframe()
        # Apply scale and position transforms on the model.
        self.model.setScale(0.25, 0.25, 0.25)
        self.model.setPos(0, 0, 0)


class STL2EGG():
    def __init__(self, in_file, out_file,showIt = False):
        #New container for datas :
        self.data = EggData()
        #New Container for vertex :
        self.vertexPool = EggVertexPool('model')
        #Adding vertexPool to the main data container :
        self.data.addChild(self.vertexPool) 
        self.load(in_file)
        self.data.writeEgg(out_file)
         
        if (showIt):
            show = AppShow(out_file)
            show.run()

    def load(self, filename):
        f = open(filename, 'r')
        try:
            header = f.read(6).decode('utf-8')
            isASCII = ( header== 'solid ')
            if isASCII:
                self.name = f.readline().decode('utf-8')
                self.parseASCII(f)
            else:
                f.close
                f = open(filename, 'rb')
                self.parseBin(f)
        except:
            f.close
            f = open(filename, 'rb')
            self.parseBin(f)


    def getName(self):
        return self.name
            
           
    def readVector(self, data):
        v = EggVertex()
        x,y,z = struct.unpack('fff', data)        
        v.setPos(Point3D(x,y,z))
        return v 
                  
    def parseBin(self, f):
        print("Parsing Bin File")
        Header = f.read(80)
        Nb_Face = struct.unpack('i', f.read(4))[0]
        # Reading Number of Triangle
        print("Number of triangles : %i" % (Nb_Face))
        for i in range(0,Nb_Face):
            self.poly = EggPolygon()
            self.data.addChild(self.poly)
            # Normal struct
            normal = self.readVector(f.read(12))
            u = self.readVector(f.read(12))
            v = self.readVector(f.read(12))
            w = self.readVector(f.read(12))
            attrib = struct.unpack('H', f.read(2))[0]   # Attributes
            #Adding Vertex to Triangle 
            self.poly.addVertex(self.vertexPool.addVertex(u))
            self.poly.addVertex(self.vertexPool.addVertex(v))
            self.poly.addVertex(self.vertexPool.addVertex(w))
            self.poly.recomputePolygonNormal()
            self.poly.setColor( VBase4( 0.0, 0.0, 0.5, 0.5) )
            #~ print("u: %s, v: %s, w: %s" % (u,v,w))
            

    def parseASCII(self,f ):       
        for line in f:
            line = line.lower().strip()
            commande = line.split(" ")
            Nb_Param = len(commande)
            try:
                {'facet'    : self.facet,
                 'outer'    : self.outer,
                 'vertex'   : self.vertex,
                 'endloop'  : self.endloop,
                 'endfacet' : self.endfacet}[commande[0]](commande,Nb_Param)
            except KeyError:
                # Command unknown or error
                pass
            
    def facet(self,commande,Nb_Param):

        if (Nb_Param==5 and commande[1] == "normal"):
            #We are Ignoring normal --> will be compute later
            #Creating a new polygon :
            self.poly = EggPolygon()
            self.data.addChild(self.poly)
                        
    def outer(self,commande,Nb_Param):
        pass
            
    def vertex(self,commande,Nb_Param):
        if (Nb_Param==4):
            x,y,z = float(commande[1]),float(commande[2]),float(commande[3])
            if (self.poly != None):
                #Creating a new vertex with coords :
                v = EggVertex()
                v.setPos(Point3D(x,y,z))
                #Adding the new Vertex to the polygon :
                self.poly.addVertex(self.vertexPool.addVertex(v))
 
                     
    def endloop(self,commande,Nb_Param):
        #End of the Loop : 
        self.poly.recomputePolygonNormal()
        #As STL file don't contain colors :
        self.poly.setColor( VBase4( 0.0, 0.0, 0.5, 0.5) )

            
    def endfacet(self,commande,Nb_Param):
        pass
        #end of the facet

if __name__ == "__main__":
    show = False
    if len(sys.argv) == 4:
        if sys.argv[3]=='--show':
            show=True
    try:
        file_in = sys.argv[1]
        file_out = sys.argv[2]
    except:
        print("Usage : python stl2egg filename_in filename_out [--show]")
        exit()
    
    app = STL2EGG(file_in, file_out, show)