import cv2

def generateFontRom():
    strName = "Anonymous.png"
    #strName = "lucidagrande.jpg"
    strName = "tut4-2.png"
    im = cv2.imread( "data/" + strName)
    
    if( strName == "Anonymous.png" ):
        ox = 0; # origin
        oy = 3;
        sx=26; # size letter
        sy=32;
        ex = 1; # size interletter
        ey = 24;

    if( strName == "tut4-2.png" ):
        im = cv2.pyrDown( im ); # PyrDown only divide by 2
        ox = 0; # origin
        oy = 0;
        sx=16; # size letter
        sy=16;
        ex = 0; # size interletter
        ey = 0;
        
        sx/=2;
        sy/=2;
    
    for j in range(16):
        for i in range(16):
            x = ox+i*(sx+ex);
            y = oy+j*(sy+ey);
            cv2.rectangle( im, (x, y), (x+sx, y+sy), (0,0,255));
    
    cv2.imshow( "im", im );
    cv2.waitKey(0);
    
# generateFontRom - end
    
    
    
    
generateFontRom();