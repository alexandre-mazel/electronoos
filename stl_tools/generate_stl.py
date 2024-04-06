import stl
import view_stl_vtk

def generateCube(o, center, size=10):
    
    n=size//2

    # bottom
    o.addTriangle((-n,-n,-n),(-n,+n,-n),(+n,-n,-n))
    o.addTriangle((+n,+n,-n),(-n,+n,-n),(+n,-n,-n))
    
    o.addTriangle((-n,-n,-n),(-n,+n,-n),(-n,-n,+n))
    o.addTriangle((-n,+n,+n),(-n,+n,-n),(-n,-n,+n))
    
    o.addTriangle((+n,+n,-n),(+n,-n,-n),(+n,-n,+n))
    o.addTriangle((+n,+n,+n),(+n,+n,-n),(+n,-n,+n))
    
    o.addTriangle((-n,+n,-n),(+n,+n,-n),(-n,+n,+n))
    o.addTriangle((+n,+n,-n),(+n,+n,+n),(-n,+n,+n))
    
    o.addTriangle((-n,-n,-n),(+n,-n,-n),(-n,-n,+n))
    o.addTriangle((+n,-n,-n),(+n,-n,+n),(-n,-n,+n))

    # top
    o.addTriangle((-n,-n,+n),(-n,+n,+n),(+n,-n,+n))
    o.addTriangle((+n,+n,+n),(-n,+n,+n),(+n,-n,+n))
        
    return o
    
def test():
    o = stl.StlObject()
    generateCube(o,(10,10,10),10)
    if 1:
        strFilename = "generated.stl"
        o.saveToStl(strFilename)
        view_stl_vtk.showStl(strFilename,bDrawingTechnic=True)
        
test()