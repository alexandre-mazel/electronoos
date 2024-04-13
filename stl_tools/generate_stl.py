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

def generateParaRot(o, center, size, rx=0, ry=0, rz=0):
    centx = center[0]
    centy = center[1]
    centz = center[2]
    
    m = size[0]/2
    n = size[1]/2
    h = size[2]/2
    
    rx = rx *pi/180
    ry = ry *pi/180
    rz = rz *pi/180
    
    xa = -m; ya = -n; za = -h
    xb = -m; yb = +n; zb = -h
    xc = +m; yc = -n; zc = -h
    xd = +m; yd = +n; zd = -h
    
    xe = -m; ye = -n; ze = +h
    xf = -m; yf = +n; zf = +h
    xg = +m; yg = -n; zg = +h
    xh = +m; yh = +n; zh = +h
    
    # rotx
    # xa = xa*cos(rx)-za*sin(rx); za=za*cos(rx)+xa*sin(rx) # NB: don't change za before doing both computation
    xa,za = xa*cos(rx)-za*sin(rx), za*cos(rx)+xa*sin(rx)
    xb,zb = xb*cos(rx)-zb*sin(rx), zb*cos(rx)+xb*sin(rx)
    xc,zc = xc*cos(rx)-zc*sin(rx), zc*cos(rx)+xc*sin(rx)
    xd,zd = xd*cos(rx)-zd*sin(rx), zd*cos(rx)+xd*sin(rx)

    #roty
    ya,za = ya*cos(ry)-za*sin(ry), za*cos(ry)+ya*sin(ry)
    yb,zb = yb*cos(ry)-zb*sin(ry), zb*cos(ry)+yb*sin(ry)
    yc,zc = yc*cos(ry)-zc*sin(ry), zc*cos(ry)+yc*sin(ry)
    yd,zc = yd*cos(ry)-zd*sin(ry), zd*cos(ry)+yd*sin(ry)
    
    #offset
    xa += centx; ya += centy; za += centz
    xb += centx; yb += centy; zb += centz
    xc += centx; yc += centy; zc += centz
    xd += centx; yd += centy; zd += centz
    
    
    
    # rotx
    xe,ze = xe*cos(rx)-ze*sin(rx), ze*cos(rx)+xe*sin(rx)
    xf,zf = xf*cos(rx)-zf*sin(rx), zf*cos(rx)+xf*sin(rx)
    xg,zg = xg*cos(rx)-zg*sin(rx), zg*cos(rx)+xg*sin(rx)
    xh,zh = xh*cos(rx)-zh*sin(rx), zh*cos(rx)+xh*sin(rx)
    
    #roty
    ye,ze = ye*cos(ry)-ze*sin(ry), ze*cos(ry)+ye*sin(ry)
    yf,zf = yf*cos(ry)-zf*sin(ry), zf*cos(ry)+yf*sin(ry)
    yg,zg = yg*cos(ry)-zg*sin(ry), zg*cos(ry)+yg*sin(ry)
    yh,zh = yh*cos(ry)-zh*sin(ry), zh*cos(ry)+yh*sin(ry)
    
    #offset
    xe += centx; ye += centy; ze += centz
    xf += centx; yf += centy; zf += centz
    xg += centx; yg += centy; zg += centz
    xh += centx; yh += centy; zh += centz


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
    
def generateRing(o, center, hole_radius, disk_w, disk_h, rx=0, ry=0, rz=0, circ = 2*pi ):
    """
    a cylinder with a hole in it.
    the base is in the Oxy plane (Ox is the seg=0 axis)(ou alors c'est Oy)
    
    - rx: rotation around x axis (degrees)
    - ry: ...
    - rz: ... applied first (decay of seg)
    - circ: put less than 2pi to limit the completness of the ring (in rad!)
    - disk_w: width of disk
    
    """
    disk_h /= 2 # offset around center
    
    step = pi/128
    seg = 0 # advancing in the disk
    
    rx = rx *pi/180
    ry = ry *pi/180
    rz = rz *pi/180

    
    while seg < circ:
        d1 = hole_radius
        d2 = hole_radius+disk_w
        #~ p1 = center[0]+d1*cos(seg+rz), center[1]+d1*sin(seg+rz),center[2]-disk_h
        #~ p2 = center[0]+d2*cos(seg+rz), center[1]+d2*sin(seg+rz),center[2]-disk_h
        #~ p3 = center[0]+d1*cos(seg+rz+step), center[1]+d1*sin(seg+rz+step),center[2]-disk_h
        #~ p4 = center[0]+d2*cos(seg+rz+step), center[1]+d2*sin(seg+rz+step),center[2]-disk_h

        #~ p1 = p1[0]*cos(rx)*cos(ry), p1[1]*cos(rx)*cos(ry), p1[2]*sin(rx)*sin(ry)
        #~ p2 = p2[0]*cos(rx)*cos(ry), p2[1]*cos(rx)*cos(ry), p2[2]*sin(rx)*sin(ry)
        #~ p3 = p3[0]*cos(rx)*cos(ry), p3[1]*cos(rx)*cos(ry), p3[2]*sin(rx)*sin(ry)
        #~ p4 = p4[0]*cos(rx)*cos(ry), p4[1]*cos(rx)*cos(ry), p4[2]*sin(rx)*sin(ry)
        
        p1 = d1*cos(seg+rz), d1*sin(seg+rz),-disk_h
        p2 = d2*cos(seg+rz), d2*sin(seg+rz),-disk_h
        p3 = d1*cos(seg+rz+step), d1*sin(seg+rz+step),-disk_h
        p4 = d2*cos(seg+rz+step), d2*sin(seg+rz+step),-disk_h
        
        # rotx
        p1 = p1[0]*cos(rx)-p1[2]*sin(rx), p1[1], p1[2]*cos(rx)+p1[0]*sin(rx)
        p2 = p2[0]*cos(rx)-p2[2]*sin(rx), p2[1], p2[2]*cos(rx)+p2[0]*sin(rx)
        p3 = p3[0]*cos(rx)-p3[2]*sin(rx), p3[1], p3[2]*cos(rx)+p3[0]*sin(rx)
        p4 = p4[0]*cos(rx)-p4[2]*sin(rx), p4[1], p4[2]*cos(rx)+p4[0]*sin(rx)
        
        #roty
        p1 = p1[0], p1[1]*cos(ry)-p1[2]*sin(ry), p1[2]*cos(ry)+p1[1]*sin(ry)
        p2 = p2[0], p2[1]*cos(ry)-p2[2]*sin(ry), p2[2]*cos(ry)+p2[1]*sin(ry)
        p3 = p3[0], p3[1]*cos(ry)-p3[2]*sin(ry), p3[2]*cos(ry)+p3[1]*sin(ry)
        p4 = p4[0], p4[1]*cos(ry)-p4[2]*sin(ry), p4[2]*cos(ry)+p4[1]*sin(ry)
        
        #offset
        p1 = center[0] + p1[0], center[1] + p1[1], center[2] + p1[2]
        p2 = center[0] + p2[0], center[1] + p2[1], center[2] + p2[2]
        p3 = center[0] + p3[0], center[1] + p3[1], center[2] + p3[2]
        p4 = center[0] + p4[0], center[1] + p4[1], center[2] + p4[2]

        
        # base
        o.addQuad(p1,p2,p4,p3)

        #~ p5 = center[0]+d1*cos(seg+rz),center[1]+d1*sin(seg+rz),center[2]+disk_h
        #~ p6 = center[0]+d2*cos(seg+rz),center[1]+d2*sin(seg+rz),center[2]+disk_h
        #~ p7 = center[0]+d1*cos(seg+rz+step),center[1]+d1*sin(seg+rz+step),center[2]+disk_h
        #~ p8 = center[0]+d2*cos(seg+rz+step),center[1]+d2*sin(seg+rz+step),center[2]+disk_h
        
        
        p5 = d1*cos(seg+rz), d1*sin(seg+rz),+disk_h
        p6 = d2*cos(seg+rz), d2*sin(seg+rz),+disk_h
        p7 = d1*cos(seg+rz+step), d1*sin(seg+rz+step),+disk_h
        p8 = d2*cos(seg+rz+step), d2*sin(seg+rz+step),+disk_h
        
        # rotx
        p5 = p5[0]*cos(rx)-p5[2]*sin(rx), p5[1], p5[2]*cos(rx)+p5[0]*sin(rx)
        p6 = p6[0]*cos(rx)-p6[2]*sin(rx), p6[1], p6[2]*cos(rx)+p6[0]*sin(rx)
        p7 = p7[0]*cos(rx)-p7[2]*sin(rx), p7[1], p7[2]*cos(rx)+p7[0]*sin(rx)
        p8 = p8[0]*cos(rx)-p8[2]*sin(rx), p8[1], p8[2]*cos(rx)+p8[0]*sin(rx)
        
        #roty
        p5 = p5[0], p5[1]*cos(ry)-p5[2]*sin(ry), p5[2]*cos(ry)+p5[1]*sin(ry)
        p6 = p6[0], p6[1]*cos(ry)-p6[2]*sin(ry), p6[2]*cos(ry)+p6[1]*sin(ry)
        p7 = p7[0], p7[1]*cos(ry)-p7[2]*sin(ry), p7[2]*cos(ry)+p7[1]*sin(ry)
        p8 = p8[0], p8[1]*cos(ry)-p8[2]*sin(ry), p8[2]*cos(ry)+p8[1]*sin(ry)
        
        #offset
        p5 = center[0] + p5[0], center[1] + p5[1], center[2] + p5[2]
        p6 = center[0] + p6[0], center[1] + p6[1], center[2] + p6[2]
        p7 = center[0] + p7[0], center[1] + p7[1], center[2] + p7[2]
        p8 = center[0] + p8[0], center[1] + p8[1], center[2] + p8[2]

        
        # top
        o.addQuad(p5,p6,p8,p7)
        
        # inner side
        o.addQuad(p1,p3,p7,p5)
        
        # outer side
        o.addQuad(p2,p4,p8,p6)
        
            
        if seg == 0 and circ < 2*pi:
            # face of first tranche
            o.addQuad(p1,p2,p6,p5)
            pass
        
        
        seg += step
    
    if circ < 2*pi:
        # face of last tranche
        o.addQuad(p3,p4,p8,p7)
        pass
        
        
# generateRing - end

def generateBlangle(o,thick, width, diam, lenborder, angle_racle = 0 ):
    # la piece pour Vincent
    
    diam /= 2
    generateRing(o,(0,-width/3,0),diam,disk_w=thick,disk_h=width/3,rx=0,ry=90,rz=30,circ=1*pi/3)
    generateRing(o,(0,width/3,0),diam,disk_w=thick,disk_h=width/3,rx=0,ry=90,rz=30,circ=1*pi/3)
    #~ generateParaRot(o,(0,0,0),(4,width,10),rx=0)
    a = 30*pi/180
    diam += lenborder/2
    cx,cy,cz = diam*cos(a),0,diam*sin(a)
    ztopbarreau = (diam-thick/2+width/2)*cos(a)
    ztopbarreau = diam-thick/2
    generateParaRot(o,(cx,cy,cz),(2,width,lenborder),rx=-60+angle_racle)
    generateParaRot(o,(0,cy,ztopbarreau),(thick,width,lenborder),rx=90)
    #~ generateParaRot(o,(0,0,0),(4,width,10),rx=90)
    return o
    
    
def test():
    o = stl.StlObject()
    if 0:
        generateParaCentered(o)
        generatePara(o,(0,0,5),(10,20,10))
        generatePara(o,(0,0,15),(4,2,10))
        
    if 0:
        generateRing(o,(3,5,0),5,10,20)
        #~ generateRing(o,(10,10,-10),5,10,20)
        #~ generateRing(o,(5,5,32),2,11,23,rz=15,circ=pi*4/3)
        generateRing(o,(0,0,30),2,11,23,rx=25,circ=pi*21/12)
        generateRing(o,(0,0,60),2,11,23,rx=45,circ=pi*4/3)
        generateRing(o,(0,0,90),2,11,23,rx=90,circ=pi*4/3)
        generateRing(o,(0,0,120),2,11,23,ry=45,circ=pi*4/3)
        generateRing(o,(0,0,150),2,11,23,rx=45,ry=45,circ=pi*4/3)
        
    if 0:
        # une pile de papier toilette
        for i in range(5):
            generateRing(o,(3,5,i*22),5,10,20)
            
    if 0:
        # une rotation de papier toilette
        for i in range(7):
            generateRing(o,(3,5,i*22),5,10,20,rx=i*15)
            generateRing(o,(3,5,-i*22),5,10,20,rx=i*15,ry=i*15)
            
    if 1:
        # la piece pour Vincent
        generateBlangle(o, thick=4, width = 20, diam = 120, lenborder=8)
        o.move((0,30,0))
        generateBlangle(o, thick=4, width = 20, diam = 160, lenborder=8, angle_racle=-20)
    
    
    if 1:
        strFilename = "generated.stl"
        o.saveToStl(strFilename)
        view_stl_vtk.showStl(strFilename,bDrawingTechnic=True)
        
test()