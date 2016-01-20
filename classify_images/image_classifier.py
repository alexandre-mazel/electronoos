import cv2
import os

import PIL
import PIL.Image
#~ print( dir(PIL))
#~ print PIL.VERSION

import PIL.ExifTags

#~ from PIL.ExifTags import TAGS
#~ print TAGS[0x010e]

#~ from PIL.ExifTags import GPSTAGS
#~ print GPSTAGS[20]
#~ exit()

def generateExifNameToTagNum():
    PIL.ExifTags.tag2Num = dict()
    for num, name in PIL.ExifTags.TAGS.iteritems():
        PIL.ExifTags.tag2Num[name] = num 

generateExifNameToTagNum()    

def getShootDateAndApnModel( strImgFilename ):
    """
    return an array of interesting information related to a picture
    """
    #~ print PIL.ExifTags.TAGS
    #~ print PIL.ExifTags.tag2Num
    #~ print exif_data    
    #~ print exif_data[PIL.ExifTags.tag2Num["Model"]]
    
    img = PIL.Image.open(strImgFilename)
    exif_data = img._getexif()
    strDate = None
    strCameraName = None
    try:
        strCameraName = exif_data[PIL.ExifTags.tag2Num["Model"]]
    except: pass
    
    try:
        strDate = exif_data[PIL.ExifTags.tag2Num["DateTimeDigitized"]]
    except: pass
    try:
        strDate = exif_data[PIL.ExifTags.tag2Num["DateTime"]]
    except: pass
    try:
        strDate = exif_data[PIL.ExifTags.tag2Num["DateTimeOriginal"]]
    except BaseException, err: print err
    return strDate, strCameraName
    

# getShootDateAndApnModel - end
    
print getShootDateAndApnModel(  "/home/a/recup3//recup_dir.187/f606058464.jpg" );
exit(0);

def classifyPath( strPathSrc, strPathDest ):
        for file in os.listdir( strPathSrc ):
            strSrc = strPathSrc + "/" + file
            if( os.path.isdir( strSrc ) ):
                classifyPath( strSrc, strPathDest )
            else:
                print( "Reading: %s" % strSrc ),
                im = cv2.imread( strSrc )
                sy,sx,c = im.shape
                h = min(sy,sx)
                w = max(sy,sx)
                print( "w: %s, h: %s" % (w,h) ),
                bAnalyse = False
                if( w == 2496 and h == 1664 ):
                    print( "Canon" ),
                    bAnalyse = True
                if( w > 1024 and h > 768 ):
                    print( "Big enough" ),
                    bAnalyse = True
                if( bAnalyse ):
                    exit(0)
                    
                    
                print( "" )



classifyPath( "/home/a/recup3/", "/tmp/classified/" )
