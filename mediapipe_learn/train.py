import math
import os

anIdxChests = [12,11,23,24]
anIdxWrists = [16,15] # Left then Right, par rapport a la camera

def dist3D(a,b):
    # return sqrt( (b[0]-a[0])*(b[0]-a[0]) + (b[1]-a[1])*(b[1]-a[1]) + (b[2]-a[2])*(b[2]-a[2]) )
    # return sqrt( pow( (b[0]-a[0]) ) + pow( (b[1]-a[1]) ) + pow( (b[2]-a[2]) )  )
    return math.sqrt( (b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2 )

def vectNorm3D(a,b,size):
    return [ (b[0]-a[0])/size, (b[1]-a[1])/size, (b[2]-a[2])/size ]
    
def sum3D(a,b):
    c = [ a[0]+b[0], a[1]+b[1], a[2]+b[2] ]
    return c
    
def div3D(a,k):
    c = [ a[0] / k, a[1] / k, a[2] / k ]
    return c
    
def computeBaryChest(dataForOneImage):
    bary = [0,0,0]
    for idx in anIdxChests:
        for pt in range(3):
            bary[pt] += dataForOneImage[idx][pt]
    for pt in range(3):
        bary[pt] /= len(anIdxChests)
    return bary
    
def computeSizeChest(dataForOneImage):
    diag1 = dist3D(dataForOneImage[anIdxChests[0]],dataForOneImage[anIdxChests[2]])
    diag2 = dist3D(dataForOneImage[anIdxChests[1]],dataForOneImage[anIdxChests[3]])

    return (diag1+diag2)/2

def loadFile(strFilename):
    print("\nINF: loadFile '%s'" % strFilename )
    f = open(strFilename,"rt")
    allImages = []
    nSizeAnalyse = 120
    while 1:
        buf = f.readline()
        if(len(buf)<2): break
        #print(buf)
        dataForOneImage = eval(buf)
        #print(dataForOneImage)
        #print(dataForOneImage[0])
        allImages.append(dataForOneImage)
        if len(allImages)==nSizeAnalyse:
            print("got %s images, computing..." % (len(allImages)))
            avgHandL = [0,0,0]
            avgHandR = [0,0,0]
            for i in range(nSizeAnalyse):
                bary = computeBaryChest(allImages[i])
                size = computeSizeChest(allImages[i])
                #~ print("bary: %s, size: %s" % (bary,size) )
                vHandL = vectNorm3D(allImages[i][anIdxWrists[0]],bary,size)
                vHandR = vectNorm3D(allImages[i][anIdxWrists[1]],bary,size)
                avgHandL = sum3D( avgHandL, vHandL )
                avgHandR = sum3D( avgHandR, vHandR )
            avgHandL = div3D( avgHandL, nSizeAnalyse )
            avgHandR = div3D( avgHandR, nSizeAnalyse )
            print("avgHandL: %s" % avgHandL )
            print("avgHandR: %s" % avgHandR )
            allImages = []


def trainAll():
    # loop all folders
    for parentFolder in ["C:/seq_vid2/","D:/seq_vid/"]:
        for folders in os.listdir(parentFolder):
            if not os.path.isdir(parentFolder+folders):
                continue
                
            for f in os.listdir(parentFolder+folders):
                if not ".skl" in f:
                    continue
                print("DBG: %s" % f)
                loadFile(parentFolder+folders+"/"+f)


def test():
    strPath = "C:/seq_vid2/sms/"
    strPathD = "D:/seq_vid/eat/"
    strFile = strPath + "sms_01.skl"
    loadFile(strFile)
    strFile = strPath + "sms_02.skl"
    loadFile(strFile)

    strFile = strPathD + "eat_01.skl"
    loadFile(strFile)
    
trainAll()