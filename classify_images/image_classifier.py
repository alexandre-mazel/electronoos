import cv2
import os
import shutil

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

def utfToAscii(strTxt, bPrintableOnly = False ):
    udata=strTxt.decode("utf-8")
    asciidata=udata.encode("ascii","ignore")
    
    # remove char < 1
    strOut = ""
    nMin = 1
    if( bPrintableOnly ):
        nMin = 14
    for i in range(len(asciidata) ):
        if( ord(asciidata[i]) >= nMin ):
            strOut += asciidata[i]            
    return strOut
    
def createDirectoryForFile( strName ):
    """
    Create all the directory required to create a file.
    eg: /tmp/tutu/toto/image.jpg will create /tmp/tutu/ and /tmp/tutu/toto/
    """
    strDir, strFilename = os.path.split(strName)
    try:
        os.makedirs( strDir )
    except: pass

def generateExifNameToTagNum():
    """
    Add to PIL library a dictionnary of name and index of tag
    """
    PIL.ExifTags.tag2Num = dict()
    for num, name in PIL.ExifTags.TAGS.iteritems():
        PIL.ExifTags.tag2Num[name] = num 

generateExifNameToTagNum()    

def getShootDateAndApnModel( strImgFilename ):
    """
    extract interesting information related to a picture (None if not)
    return [date of picture, camera name, owner name], None, if one of them is empty
    """
    #~ print PIL.ExifTags.TAGS
    #~ print PIL.ExifTags.tag2Num
    #~ print exif_data[PIL.ExifTags.tag2Num["Model"]]
    
    img = PIL.Image.open(strImgFilename)
    try:
        exif_data = img._getexif()
    except BaseException, err:
        print( "WRN: exif reading error: " + str(err) )
        return[ "1900", "exif_error", None ]
        
    if( exif_data == None ):
        return [None, None, None]
    print exif_data        
    strDate = None
    strCameraName = None
    strCameraOwnerName = None
    try:
        strCameraName = exif_data[PIL.ExifTags.tag2Num["Model"]]
    except: pass
    try:
        strCameraName = exif_data[PIL.ExifTags.tag2Num["CameraOwnerName"]]
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
    
    
    return [strDate, strCameraName, strCameraOwnerName]
    

# getShootDateAndApnModel - end
    
#~ print getShootDateAndApnModel(  "/home/a/recup3//recup_dir.187/f606058464.jpg" );
#~ print getShootDateAndApnModel(  "/home/a/recup3//recup_dir.81/f358798112.jpg" )
#~ print getShootDateAndApnModel(  "/home/a/recup3//recup_dir.10/f58786880.jpg" )
#~ exit(1)

def classifyPath( strPathSrc, strPathDest ):
    """
    Take a raw path containing image with mostly exif tagged files, and generate a classified path with subfolder classified by apn, model and year of shoot
    """
    cpt = 0
    cptMid = 0
    cptLarge = 0
    cptExif = 0
    cptWrong = 0
    for file in os.listdir( strPathSrc ):
        cpt += 1
        strSrc = strPathSrc + "/" + file
        if( os.path.isdir( strSrc ) ):
            classifyPath( strSrc, strPathDest )
        else:
            print( "Reading: %s" % strSrc ),
            im = cv2.imread( strSrc )
            if( im == None ):
                cptWrong += 1
                continue
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
            elif( w >= 640 and h >= 480 ):
                cptMid += 1
            if( bAnalyse ):
                cptLarge += 1
                dummy, strExt = os.path.splitext(file)                
                strDate, strModel, strOwner = getShootDateAndApnModel( strSrc )
                print( "\nstrDate: '%s', strModel: '%s'" % ( strDate, strModel) )
                if( strDate != "" and strDate != None ):
                    cptExif += 1
                    strDateClean = strDate.replace( ":", "-" )
                    strDateClean = strDateClean.replace( " ", "_-_" )
                    strNum = "%03d"%(cpt%1000);
                    strYear = strDateClean[:4]
                    if strModel == None:
                        strModel = "no_model"
                    if strOwner == None:
                        strOwner = ""
                    else:
                        strOwner = '_' + strOwner.replace( ' ', '_' )
                    strSubDir = strModel.replace( ' ' , '_' ) + strOwner + '/' + strYear + '/'
                    strDest = strPathDest + '/' + strSubDir + strDateClean + '_' + strNum + strExt
                    strDest = utfToAscii( strDest, bPrintableOnly = True )
                else:
                    strNum = "%09d"%cpt;
                    strDest = strPathDest + "/no_exif/" + strNum + strExt
                createDirectoryForFile( strDest )
                print( "\nINF: saving to '%s'" % strDest ),
                #shutil.copyfile( strSrc, strDest )
                os.rename( strSrc, strDest )
                
                
            print( "" )
            print( "cpt: %d, med: %d, large: %d (exif: %d)" % (cpt, cptMid, cptLarge, cptExif) )
            
     # for - end
     
    print( "cpt: %d, med: %d, large: %d (exif: %d) + all subdirs..." % (cpt, cptMid, cptLarge, cptExif) )
    
# classifyPath - end

classifyPath( "/home/a/recup3/", "/home/a/img_classified/" )
