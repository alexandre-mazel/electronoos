"""
Generate C code with static data from image file (eg for arduino)
"""
import cv2
import sys

def generateImg( aListImg, w=14, h=8, nNbrBits=24 ):
    """
    Will generate a matrix of BGR images.
    - w: resize to width, if -1 => keep original size
    - nNbrBits: 
        - 24 => 1 byte per channel
        - 15 => 5 bits per channel
        - 4 => palette de 16 couleurs
    """
    
    bOneArrayPerImage = 1
    bUseDifferentPaletteForEachImage = 1
    
    
    print( "INF: generateImg: generating from image(s): %s" % str(aListImg) )
    
    bRender = 0;
    aPalette = list(); # idx => RGB
    strOut = "// generated by generate_img.py using %s\n" % str(aListImg);
    strDataType = "char"
    if nNbrBits == 15:
        strDataType = "short int"
    if nNbrBits == 4:
        strDataType = "char"
    strOptionnalNumber = ""
    if bOneArrayPerImage:
        strOptionnalNumber = "_1"
    strOut += "unsigned %s aImgs%s[] = {\n" % (strDataType,strOptionnalNumber);
    
    nNbrDataOutputted = 0;
    
    w_param = w
    h_param = h
    
    strOutHeaderMultiArray = ""


    for nNumImage, strFilename in enumerate(aListImg):
        print( "INF: opening '%s'" % strFilename );
        img = cv2.imread( strFilename );
        if img is None:
            print("ERR: opening '%s' has failed" % strFilename)
            return False
    
        w = w_param
        h = h_param
        
        if w == -1: w = img.shape[1]
        if h == -1: h = img.shape[0]
        
        print("INF: img is %dx%d" % (w,h))
        
        if nNbrBits == 4 and (w%2) == 1:
            print("ERR: generateImg can't generate image with odd width (w:%d)" % w )
            return False

        if w != img.shape[1] or h != img.shape[0]:
            img = cv2.resize(img, (w, h)) 
        
        if( bRender ):
            cv2.imshow( "imdraw", img );
            cv2.waitKey(0);
            
        if bUseDifferentPaletteForEachImage:
            aPalette = list();
            
        for j in range(h):
            strOut += "// img: %d, %s, line %d\n" % (nNumImage,strFilename, j);
            for i in range(w):
                val = img[j,i]
                if nNbrBits == 24:
                    strOut += "0x%02X, 0x%02X, 0x%02X,\n" % (val[0], val[1], val[2]); # B, V, R
                    nNbrDataOutputted += 3
                elif nNbrBits == 15:
                    col15 =  ((val[0]>>3)<<10 ) | ((val[1]>>3)<<5 ) | ((val[2]>>3))
                    strOut += "0x%06X,\n" % (col15);
                    nNbrDataOutputted += 2
                elif nNbrBits == 4:
                    if i*2>=w:
                        break
                    col4 = 0
                    for numpix in range(2):
                        val = img[j,i*2+numpix]
                        # dither
                        nDitherFactor = 5
                        val = list(val)
                        for chan in range(3):
                            b = (((val[chan]+1)>>nDitherFactor)<<nDitherFactor)-1
                            if b < 0:
                                b = 0
                            val[chan] = b
                                
                        # find color in palette
                        for k,v in enumerate(aPalette):
                            if v == val:
                                break
                        else:
                            aPalette.append(val)
                            if(len(aPalette)>16):
                                print("ERR: Too much color in this image for a 16 colors palette (at pixel %dx%d)" % (i,j))
                                print("ERR: current palette: %s" % str(aPalette))
                                return False
                            k = len(aPalette)-1
                        col4 |= k<<(numpix*4)
                    strOut += "0x%02X,\n" % (col4);  
                    nNbrDataOutputted += 1
            strOut += "\n";
        # end one image
        
        if bOneArrayPerImage:
            strOut += "};\n";
            strOut += "// data outputted = %dB\n\n" % (nNbrDataOutputted);
            nNbrDataOutputted = 0;
            
            strOutHeaderMultiArray += "\n"
            strOutHeaderMultiArray += "#define IMG_%d_SIZE_X %d\n" % (nNumImage+1,w);
            strOutHeaderMultiArray += "#define IMG_%d_SIZE_Y %d\n" % (nNumImage+1,h);
            strOutHeaderMultiArray += "extern unsigned %s aImgs_%d[];\n" % (strDataType,nNumImage+1);
            if len(aPalette)>0:
                strOutHeaderMultiArray += "extern unsigned char aPalette_%d[];\n" % (nNumImage+1)
            
        if len(aPalette)>0 and bUseDifferentPaletteForEachImage:
            strOut += "\n"
            strOut += "unsigned char aPalette_%d[%d] = {\n// B,  V,  R\n" % (nNumImage+1, len(aPalette)*3)
            for i in range(len(aPalette)):
                col = aPalette[i]
                strOut += "0x%02x,0x%02x,0x%02x, \t// idx %d\n" % (col[0],col[1],col[2],i)
            strOut += "};\n\n"; 
            
        if bOneArrayPerImage and nNumImage+1<len(aListImg):
            strOut += "unsigned %s aImgs_%d[] = {\n" % (strDataType,nNumImage+2);
    # end all images
    
    if not bOneArrayPerImage:
        strOut += "};\n";
        strOut += "// data outputted = %dB\n" % (nNbrDataOutputted);  

    if len(aPalette)>0 and not bUseDifferentPaletteForEachImage:
        strOut += "\n"
        strOut += "unsigned char aPalette[%d] = {\n// B,  V,  R\n" % (len(aPalette)*3)
        for i in range(len(aPalette)):
            col = aPalette[i]
            strOut += "0x%02x,0x%02x,0x%02x, \t// idx %d\n" % (col[0],col[1],col[2],i)
        strOut += "};\n";        
    
        
    
    file = open("/tmp/imgs.c", "wt" );
    file.write( strOut );
    file.close();
    
    file = open("/tmp/imgs.h", "wt" );
    
    strOut = "";
    strOut += "#ifndef IMGS_H\n"
    strOut += "#define IMGS_H\n";
    strOut += "#define IMG_NBR_BITS %d\n" % nNbrBits;
    strOut += "#define IMG_NBR    %d\n" % (nNumImage+1);
    if not bOneArrayPerImage:
        strOut += "#define IMG_SIZE_X %d\n" % w;
        strOut += "#define IMG_SIZE_Y %d\n" % h;
        strOut += "extern unsigned %s aImgs[]; // putting unsigned type * generate an error: aImgs is set to 0\n" % strDataType;
        if len(aPalette)>0:
            strOut += "extern unsigned char aPalette[];\n"
    else:
        strOut += strOutHeaderMultiArray + "\n"
            
    strOut += "#endif // IMGS_H\n";
    file.write( strOut );
    file.close();
    
    print("INF: generateImg: finished, outputted to /tmp/img.h and .c")
    return True

    
# generateImg - end

def generateBunchOfImages():
    #~ strImage = "../data/house_face.jpg";
    #~ strImage = "../data/girl_face.jpg";
    #~ strImage = "../data/Pacman_HD.png";

    #~ aListImg = ["../data/house_face.jpg", "../data/girl_face.jpg", "../data/Pacman_HD.png"];

    aLogo = ["logo_atari.png", "logo_intel.png", "logo_raspberry.jpg", "logo_batman.png", "logo_nike.jpg", 
    "logo_shell.jpg","logo_chrome.png", "logo_olympic.png", "logo_superman.png", "logo_ikea.jpg", "logo_puma.jpg", "logo_target.jpg"
    ];

    aListImg = ["../data/"+i for i in aLogo];

        
    generateImg(aListImg);
    
if __name__ == "__main__":
    #~ generateBunchOfImages()
    if 1:
        # syntaxe filename [filename2] [filename3] [nbr_bits per pix=24]
        nbr_bits = 24
        listFilename = []
        for i in range(1,len(sys.argv)):
            if len(sys.argv[i])<4:
                nbr_bits = int(sys.argv[i])
            else:
                listFilename.append(sys.argv[i])
                
        generateImg(listFilename,-1,-1,nbr_bits)

