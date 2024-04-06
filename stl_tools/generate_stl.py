import stl
import view_stl_vtk

def generateParaCenter(o, size=10):
    
    m = size//3
    n = size//2
    h = 2*n

    # bottom
    o.addTriangle((-m,-n,-h),(-m,+n,-h),(+m,-n,-h))
    o.addTriangle((+m,+n,-h),(-m,+n,-h),(+m,-n,-h))
    
    o.addTriangle((-m,-n,-h),(-m,+n,-h),(-m,-n,+h))
    o.addTriangle((-m,+n,+h),(-m,+n,-h),(-m,-n,+h))
    
    o.addTriangle((+m,+n,-h),(+m,-n,-h),(+m,-n,+h))
    o.addTriangle((+m,+n,+h),(+m,+n,-h),(+m,-n,+h))
    
    o.addTriangle((-m,+n,-h),(+m,+n,-h),(-m,+n,+h))
    o.addTriangle((+m,+n,-h),(+m,+n,+h),(-m,+n,+h))
    
    o.addTriangle((-m,-n,-h),(+m,-n,-h),(-m,-n,+h))
    o.addTriangle((+m,-n,-h),(+m,-n,+h),(-m,-n,+h))

    # top
    o.addTriangle((-m,-n,+h),(-m,+n,+h),(+m,-n,+h))
    o.addTriangle((+m,+n,+h),(-m,+n,+h),(+m,-n,+h))
        
    return o
    
def test():
    o = stl.StlObject()
    generateParaCenter(o,10)
    #~ generatePara(o,(10,10,10),10)
    if 1:
        strFilename = "generated.stl"
        o.saveToStl(strFilename)
        view_stl_vtk.showStl(strFilename,bDrawingTechnic=True)
        
test()