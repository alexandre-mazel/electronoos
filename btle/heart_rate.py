import datetime
import time

import matplotlib.pyplot as plt

def renderHr( aData ):
    listPlot = []
    listX = []
    xLabels = []
    textLabels = []
    nMin = 200
    xMin = 0
    nPrevHour = -1
    for i in range(len(aData)):
        bpm = aData[i][-1]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        x = i
        hour =  aData[i][1]
        #x = hour
        
        listPlot.append( bpm )        
        listX.append(x)
        
        if nPrevHour != hour:
            xLabels.append(i)
            textLabels.append( str(hour) )
            nPrevHour = hour
        
        if nMin > bpm:
            nMin = bpm        
            xMin = i
        
    plt.xticks(xLabels, textLabels) # draw just new hour
    plt.plot(listX, listPlot)
    plt.ylabel('bpm')
    plt.annotate('min: ' + str(nMin), xy=(xMin, nMin), xytext=(xMin+len(aData)/10, nMin), arrowprops=dict(facecolor='black', shrink=0.05), )    
    plt.grid(True)                                                                                                                                                                                                                                                                                                              
    plt.show()    


def analyseHrFile( filename ):
    """
    Analyse a file with one data perline: 20161016_060141: 58 # 58 is the bpm
    """
    hrfile = open( filename, "rt" )
    data = hrfile.read()
    hrfile.close()
    lines = data.split( "\n" )
    hrs = [] # for each data: stamp, hour, sec since beginning, bpm
    secBegin = -1
    nMin = 200
    nMax = 0
    nSum = 0
    for line in lines:
        if len(line)<2:
            continue
        stamp, bpm = line.split( ": " )
        bpm = int(bpm)
        

        date_object = datetime.datetime.strptime( stamp, "%Y%m%d_%H%M%S" )
        timeCurr = date_object
        if secBegin == -1:
            secBegin = time.mktime(date_object.timetuple())
        sec = time.mktime(date_object.timetuple()) - secBegin
        newrec = [stamp, date_object.hour, sec, bpm]
        #print newrec
        hrs.append( newrec )
        
        if nMin > bpm:
            nMin = bpm
        if nMax < bpm:
            nMax = bpm
        nSum += bpm
    # for line
    
    print( "nMin: %s, nMax: %s, nAvg: %s" % ( nMin, nMax, nSum/len(hrs) ) )
    
    # draw it
    renderHr( hrs )
    
# analyseHrFile - end
    
analyseHrFile( "/tmp/alex_hr.txt" )