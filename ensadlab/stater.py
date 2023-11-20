"""
Yet another statistics tools.
Store statistics and send them to osc viewer
"""
import sys
sys.path.append("../osc_viewer")
import send_osc
import time

class Stater:
    
    def __init__( self, rRefreshTimeSec = 1, rFrameSec = 5., viewer_ip="127.0.0.1" ):
        self.rRefreshTimeSec = rRefreshTimeSec # time to send infos
        self.period = rFrameSec # time of a frame
        self.viewer_ip = viewer_ip
        self.sender = send_osc.Sender()
        self.sender.connect(viewer_ip)
        self.stop_thread = False
        
        self.reset()
        
    def __del__( self ):
        self.stopThread()
        
    def reset( self ):
        print("INF: Stater.reset")
        
        self.rSumVolTotal = 0.
        self.rSumVolHttp = 0.
        self.rSumVolHttps = 0.
        self.rSumVolArp = 0.
        self.rSumVolUdp = 0.
        
        self.nSumCptTotal = 0
        self.nSumCptHttp = 0
        self.nSumCptHttps = 0
        self.nSumCptArp = 0
        self.nSumCptUdp = 0

        self.startNewFrame()
        self.lastSend = time.time()-10000 # time last send in epoch
        self.lastStartFrame = time.time()-10000 # time in epoch
        
        self.listTotalHostDst = {} # for each ip, cpt, vol
        self.listTotalHostSrc = {}

        
    def startNewFrame( self ):
        print("INF: Stater.startNewFrame")
        self.rFrameVolTotal = 0.
        self.rFrameVolHttp = 0.
        self.rFrameVolHttps = 0.
        self.rFrameVolArp = 0.
        self.rFrameVolUdp = 0.  

        self.nFrameCptTotal = 0
        self.nFrameCptHttp = 0
        self.nFrameCptHttps = 0
        self.nFrameCptArp = 0
        self.nFrameCptUdp = 0           

    def addVolHttp(self,v):
        self.rSumVolHttp += v
        self.rSumVolTotal += v
        self.rFrameVolHttp += v
        self.rFrameVolTotal += v
        
        self.nSumCptHttp += 1
        self.nSumCptTotal += 1
        self.nFrameCptHttp += 1
        self.nFrameCptTotal += 1
        
        
    def addVolHttps(self,v):
        self.rSumVolHttps += v
        self.rSumVolTotal += v
        self.rFrameVolHttps += v
        self.rFrameVolTotal += v
        
        self.nSumCptHttps += 1
        self.nSumCptTotal += 1
        self.nFrameCptHttps += 1
        self.nFrameCptTotal += 1
        
    def addVolArp(self,v):
        self.rSumVolArp += v
        self.rSumVolTotal += v
        self.rFrameVolArp += v
        self.rFrameVolTotal += v
        
        self.nSumCptArp += 1
        self.nSumCptTotal += 1
        self.nFrameCptArp += 1
        self.nFrameCptTotal += 1
        
    def addVolUdp(self,v):
        self.rSumVolUdp += v
        self.rSumVolTotal += v
        self.rFrameVolUdp += v
        self.rFrameVolTotal += v
        
        self.nSumCptUdp += 1
        self.nSumCptTotal += 1
        self.nFrameCptUdp += 1
        self.nFrameCptTotal += 1
        
    def addSrc( self, strIp, vol ):
        """
        add src and volume in bytes
        """
        while 1:
            try:
                self.listTotalHostDst[strIP][0] = self.listTotalHostDst[strIP][0] + 1
                self.listTotalHostDst[strIP][1] = self.listTotalHostDst[strIP][1] + vol
                return
            except KeyError as err:
                self.listTotalHostDst[strIP] = [0,0]
        
    def sendLabels(self):
        labels = [      
                            "rSumVolTotal", "rSumVolHttp", "rSumVolHttps", "rSumVolArp", "rSumVolUdp",
                            "nSumCptTotal", "nSumCptHttp", "nSumCptHttps", "nSumCptArp", "nSumCptUdp",
                            "rFrameVolTotal", "rFrameVolHttp", "rFrameVolHttps", "rFrameVolArp", "rFrameVolUdp",
                            "nFrameCptTotal", "nFrameCptHttp", "nFrameCptHttps", "nFrameCptArp", "nFrameCptUdp",
        ]
        #~ 
        self.sender.sendMessage("/global_labels",labels)
        
    def update( self ):
        #~ print("update")
        if time.time()-self.lastSend > self.rRefreshTimeSec:
            values = [ 
                            self.rSumVolTotal, self.rSumVolHttp, self.rSumVolHttps, self.rSumVolArp, self.rSumVolUdp,
                            self.nSumCptTotal, self.nSumCptHttp, self.nSumCptHttps, self.nSumCptArp, self.nSumCptUdp,
                            self.rFrameVolTotal, self.rFrameVolHttp, self.rFrameVolHttps, self.rFrameVolArp, self.rFrameVolUdp,
                            self.nFrameCptTotal, self.nFrameCptHttp, self.nFrameCptHttps, self.nFrameCptArp, self.nFrameCptUdp,
                        ]
            print("INF: Stater.update: sending")
            self.lastSend = time.time()
            self.sender.sendMessage("/global",values)
            
            # src
            aList = []
            for k,v in self.listTotalHostDst.items():
                aList.append(k,v[:])
            self.sender.sendMessage("/src",values)    
            
        if time.time()-self.lastStartFrame > self.period:
            self.lastStartFrame = time.time()
            self.startNewFrame()
            
    def startUpdateLoopInTheBackground(self):
        def threaded_function(arg):
            """
            arg is the stater object
            """
            while not self.stop_thread:
                arg.update()
                time.sleep(min(arg.period,arg.rRefreshTimeSec)/10.)
            
        import threading
        self.stop_thread = False
        thread = threading.Thread(target = threaded_function, args = (self, ))
        thread.start()
        
    def stopThread( self ):
        self.stop_thread = True
        
# class Stater - end

if __name__ == "__main__":
    aStater = Stater()
    aStater.sendLabels()
    aStater.startUpdateLoopInTheBackground()
    for i in range(50):
        aStater.addVolHttp(0.1)
        time.sleep(0.1)
    aStater.stopThread()