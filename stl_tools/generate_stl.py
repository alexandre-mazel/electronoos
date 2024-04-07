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
    
def generatePara(o, center, size=10):
    
    m = size//3
    n = size//2
    h = 2*n
    
    """
       G---H
     /     / |
    E---F  |
    |     |  |     |   /
    | C---D     z  x
    |/    |/      | /
    A---B       |--y--
    
    """
    centx = center[0]
    centy = center[1]
    centz = center[2]
    
    xa = centx-m; ya = centy-n; za = centy-h
    xb = centx-m; yb = centy+n; zb = centy-h
    xc = centx+m; yc = centy-n; zc = centy-h
    xd = centx+m; yd = centy+n; zd = centy-h
    
    xe = centx-m; ye = centy-n; ze = centy+h
    xf = centx-m; yf = centy+n; zf = centy+h
    xg = centx+m; yg = centy-n; zg = centy+h
    xh = centx+m; yh = centy+n; zh = centy+h

    # bottom
    o.addTriangle((xa,ya,za),(xb,yb,zb),(xc,yc,zc))
    o.addTriangle((xd,yd,zd),(xb,yb,zb),(xc,yc,zc))
    
    o.addTriangle((-m,-n,-h),(-m,+n,-h),(-m,-n,+h))
    o.addTriangle((-m,+n,+h),(-m,+n,-h),(-m,-n,+h))
    
    o.addTriangle((+m,+n,-h),(+m,-n,-h),(+m,-n,+h))
    o.addTriangle((+m,+n,+h),(+m,+n,-h),(+m,-n,+h))
    
    o.addTriangle((-m,+n,-h),(+m,+n,-h),(-m,+n,+h))
    o.addTriangle((+m,+n,-h),(+m,+n,+h),(-m,+n,+h))
    
    o.addTriangle((-m,-n,-h),(+m,-n,-h),(-m,-n,+h))
    o.addTriangle((+m,-n,-h),(+m,-n,+h),(-m,-n,+h))

    # top
    o.addTriangle((xe,ye,ze),(xf,yf,zf),(xg,yg,zg))
    o.addTriangle((xh,yh,zh),(xf,yf,zf),(xg,yg,zg))
        
    return o
    
def test():
    o = stl.StlObject()
    #~ generateParaCenter(o,10)
    generatePara(o,(30,20,10),10)
    if 1:
        strFilename = "generated.stl"
        o.saveToStl(strFilename)
        view_stl_vtk.showStl(strFilename,bDrawingTechnic=True)
        
test()