import cv2

def generateFontRom():
    strName = "Anonymous.png"
    #strName = "lucidagrande.jpg"
    im = cv2.imread( "data/" + strName)
    
    ox = 0; # origin
    oy = 3;
    sx=26; # size letter
    sy=32;
    ex = 1; # size interletter
    ey = 24;
    
    for j in range(5):
        for i in range(16):
            x = ox+i*(sx+ex);
            y = oy+j*(sy+ey);
            cv2.rectangle( im, (x, y), (x+sx, y+sy), (0,0,255));
    
    cv2.imshow( "im", im );
    cv2.waitKey(0);
    
# generateFontRom - end
    
    
    
    
generateFontRom();