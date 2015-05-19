import cv2
import numpy as np

def generateBitmaps( strFilename, astrListOutName = None, strFolderDest = None ):
    """
    Take a big image and generate a lot of small image with part of image
    - astrListOutName: name to give to each file
    """
    im = cv2.imread( strFilename );
    imdraw = cv2.imread( strFilename );
    
    print( "INF: origin image properties: x*y*c = %d*%d*%d" % (im.shape[1],im.shape[0],im.shape[2]) );

    ox = 8; # origin
    oy = 12;
    sx = 68; # size bitmap
    sy = 72;
    ex = 6; # size inter bitmap
    ey = 2; 
    bInvertPlacing = 0
            
    
    bRender = 1
    
    if( astrListOutName == None ):
        astrListOutName = [];
        for i in range( (im.shape[0]/sy)*(im.shape[1]/sx) ):
            astrListOutName.append( str(i) + ".png" );
        
    if( strFolderDest == None ):
        strFolderDest = "/tmp/";
    
    nNbrImgOutputed = 0;
    nNumImg = 0;
    for k in range((im.shape[0]/sy)):
        for l in range((im.shape[1]/sx)):
            j = k
            i = l
            if( bInvertPlacing ):
                i = k
                j = l
            x = ox+i*(sx+ex);
            y = oy+j*(sy+ey);
            
            if( astrListOutName[nNumImg] not in [None, ""] ):
                small = np.zeros( (sy,sx,im.shape[2]), np.uint8 );
                for jj in range(sy):
                    for ii in range(sx):
                        if( y+jj < im.shape[0] and x+ii < im.shape[1] ):
                            val = im[y+jj,x+ii]
                            small[jj,ii] = val;
                        else:
                            print( "WRN: out of image for i: %d, x:%d, ii: %d, j: %d, y: %d, jj: %d" % (i,x,ii,j, y,jj) );
                cv2.imwrite( strFolderDest + astrListOutName[nNumImg], small );
                nNbrImgOutputed +=1;
                if( bRender ):
                    cv2.rectangle( imdraw, (x, y), (x+sx, y+sy), (0,0,255));
            nNumImg += 1;
    
    if(bRender):
        cv2.imshow( "imdraw", imdraw );
        cv2.waitKey(0);
        
    
# generateBitmaps - end
    
    
strSrc = "data/flags/Worldcup-Flag-Balls.jpg"

listOut = [""]*64; # could be greater than required...
listOut[17] = "flag_fr.png";
listOut[18] = "flag_de.png";
listOut[28] = "flag_es.png";
listOut[30] = "flag_us.png";
    
generateBitmaps(strSrc, listOut);


