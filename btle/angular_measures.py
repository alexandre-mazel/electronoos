import datetime
import time

import matplotlib.pyplot as plt

class EKF:
    """
    produce an Enhanced Kalman Filter on a measured variable 
    """
    def __init__( self ):
        self.R = 1. # estimate of measurement variance, change to see effect  # 0.1**2
        self.Q = 5e-4 # process variance (1e-5)
        
        self.xhat = 0.0
        self.P = 1.0
        
    def update( self, value ):
        """
        receive a value and return the filtered results
        """
        # time update
        xhatminus = self.xhat
        Pminus = self.P+self.Q

        # measurement update
        K = Pminus/( Pminus+self.R )
        self.xhat = xhatminus+K*(value-xhatminus)
        self.P = (1-K)*Pminus
        return self.xhat

        
# class EKF - end

def renderAngular( aData ):
    listPlot = []
    listPlotFiltered = []
    listPlotAveraged30 = []
    listPlotAveraged300 = []
    listX = []
    rCumulErrorEKF = 0 # compare to avg300
    rCumulErrorAvg30 = 0

    xLabels = []
    textLabels = []
    nMin = 200
    xMin = 0
    nPrevHour = -1
    ekf = EKF()
    for i in range(len(aData)):
        angle = aData[i][-1]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        x = i
        hour =  aData[i][1]
        #x = hour
        
        listX.append(x)        
        listPlot.append( angle )        
        angleFiltered = ekf.update(angle)
        listPlotFiltered.append( angleFiltered )
        angleAveraged30 = sum(listPlot[-30:])/len(listPlot[-30:])
        angleAveraged300 = sum(listPlot[-300:])/len(listPlot[-300:])
        listPlotAveraged30.append(angleAveraged30)
        listPlotAveraged300.append(angleAveraged300)
        rCumulErrorEKF += abs(angleAveraged300-angleFiltered)
        rCumulErrorAvg30 += abs(angleAveraged300-angleAveraged30)
        print( "%7.3f => %7.3f (%7.3f/%7.3f)" % (angle, angleFiltered, angleAveraged30,angleAveraged300  ) )
        
        if nPrevHour != hour:
            xLabels.append(i)
            textLabels.append( str(hour) )
            nPrevHour = hour
        
        if nMin > angle:
            nMin = angle        
            xMin = i
        
    plt.xticks(xLabels, textLabels) # draw just new hour
    plt.plot(listX, listPlot)
    plt.plot(listX, listPlotFiltered) # green
    plt.plot(listX, listPlotAveraged30) # red
    plt.plot(listX, listPlotAveraged300) # cyan
    plt.ylabel(['angle', 'filtered', 'avg'])
    plt.annotate('min: ' + str(nMin), xy=(xMin, nMin), xytext=(xMin+len(aData)/10, nMin), arrowprops=dict(facecolor='black', shrink=0.05), )    
    plt.grid(True)                                                                                                                                                                                                                                                                                                              
    plt.show()
    print( "cumulated error: rCumulErrorEKF: %7.3f, rCumulErrorAvg30: %7.3f" % (rCumulErrorEKF,rCumulErrorAvg30) )
# renderAngular - end    


def analyseAngularFile( filename ):
    """
    Analyse a file with one data perline: 20161016_060141: 6.362691 # 6.362691 is the angle
    """
    hrfile = open( filename, "rt" )
    data = hrfile.read()
    hrfile.close()
    lines = data.split( "\n" )
    hrs = [] # for each data: stamp, hour, sec since beginning, angle
    secBegin = -1
    rMin = +500
    rMax = -500
    rSum = 0
    for line in lines:
        if len(line)<2:
            continue
        stamp, angle = line.split( ": " )
        angle = float(angle)

        date_object = datetime.datetime.strptime( stamp, "%Y%m%d_%H%M%S" )
        timeCurr = date_object
        if secBegin == -1:
            secBegin = time.mktime(date_object.timetuple())
        sec = time.mktime(date_object.timetuple()) - secBegin
        newrec = [stamp, date_object.hour, sec, angle]
        #print newrec
        hrs.append( newrec )
        
        if rMin > angle:
            rMin = angle
        if rMax < angle:
            rMax = angle
        rSum += angle
    # for line
    
    print( "nbr: %s, nMin: %s, nMax: %s, nAvg: %s" % ( len(hrs), rMin, rMax, rSum/len(hrs) ) )
    
    # draw it
    renderAngular( hrs[:1000] )
    
# analyseAngularFile - end

#~ analyseAngularFile( "/home/a/Downloads/data_angle_0.txt" )
analyseAngularFile( "/home/a/Downloads/data_angle_1.txt" )
#~ analyseAngularFile( "/home/a/Downloads/data_angle_2.txt" )


