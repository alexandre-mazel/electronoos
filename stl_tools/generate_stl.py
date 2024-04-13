import stl
import view_stl_vtk
from math import pi,cos,sin

def generateParaCentered(o, xsize=10, ysize=10, hsize=10):
    
    m = xsize/2
    n = ysize/2
    h = hsize/2

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
    
# generateParaCentered - end
    
def generatePara(o, center, size):
    
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
    
    m = size[0]/2
    n = size[1]/2
    h = size[2]/2
    
    xa = centx-m; ya = centy-n; za = centz-h
    xb = centx-m; yb = centy+n; zb = centz-h
    xc = centx+m; yc = centy-n; zc = centz-h
    xd = centx+m; yd = centy+n; zd = centz-h
    
    xe = centx-m; ye = centy-n; ze = centz+h
    xf = centx-m; yf = centy+n; zf = centz+h
    xg = centx+m; yg = centy-n; zg = centz+h
    xh = centx+m; yh = centy+n; zh = centz+h

    a = (xa,ya,za)
    b = (xb,yb,zb)
    c = (xc,yc,zc)
    d = (xd,yd,zd)
    e = (xe,ye,ze)
    f = (xf,yf,zf)
    g = (xg,yg,zg)
    h = (xh,yh,zh)
    
    # bottom
    o.addTriangle(a,b,c)
    o.addTriangle(d,b,c)
    
    o.addTriangle(a,c,e)
    o.addTriangle(c,e,g)
    
    o.addTriangle(b,d,f)
    o.addTriangle(d,f,h)
    
    o.addTriangle(a,b,e)
    o.addTriangle(b,e,f)
    
    o.addTriangle(c,d,h)
    o.addTriangle(c,h,g)

    # top
    o.addTriangle(e,f,g)
    o.addTriangle(h,f,g)
        
    return o
    
# generatePara - end
    
def generateRing(o, center, hole_radius, disk_w, disk_h, alpha=0, beta=0 ):
    """
    a cylinder with a hole in it.
    - alpha and beta: angle of the radial axis.
        - alpha: angle with x (degrees)
        - beta: angle with y (degrees)
    - disk_w: width of disk
    """
    disk_h /= 2 # offset around center
    
    step = pi/240
    seg = 0 # advancing in the disk
    while seg < pi*2:
        d1 = hole_radius
        d2 = hole_radius+disk_h
        p1 = center[0]+d1*cos(seg),center[1]+d1*sin(seg),center[2]-disk_h
        p2 = center[0]+d2*cos(seg),center[1]+d2*sin(seg),center[2]-disk_h
        p3 = center[0]+d1*cos(seg+step),center[1]+d1*sin(seg+step),center[2]-disk_h
        p4 = center[0]+d2*cos(seg+step),center[1]+d2*sin(seg+step),center[2]-disk_h
        
        # base
        o.addQuad(p1,p2,p4,p3)


        p5 = center[0]+d1*cos(seg),center[1]+d1*sin(seg),center[2]+disk_h
        p6 = center[0]+d2*cos(seg),center[1]+d2*sin(seg),center[2]+disk_h
        p7 = center[0]+d1*cos(seg+step),center[1]+d1*sin(seg+step),center[2]+disk_h
        p8 = center[0]+d2*cos(seg+step),center[1]+d2*sin(seg+step),center[2]+disk_h
        
        # top
        o.addQuad(p5,p6,p8,p7)
        
        # inner side
        o.addQuad(p1,p3,p7,p5)
        
        # outer side
        o.addQuad(p2,p4,p8,p6)
        
        
        seg += step
        
# generateRing - end
    
    
    
    
def test():
    o = stl.StlObject()
    #~ generateParaCentered(o)
    #~ generatePara(o,(0,0,5),(10,20,10))
    #~ generatePara(o,(0,0,15),(4,2,10))
    generateRing(o,(3,5,10),5,10,20)
    if 1:
        strFilename = "generated.stl"
        o.saveToStl(strFilename)
        view_stl_vtk.showStl(strFilename,bDrawingTechnic=True)
        
test()