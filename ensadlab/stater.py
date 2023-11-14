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
        self.startNewFrame()
        self.lastSend = time.time()-10000 # time last send in epoch
        self.lastStartFrame = time.time()-10000 # time in epoch

        
    def startNewFrame( self ):
        print("INF: Stater.startNewFrame")
        self.rFrameVolTotal = 0.
        self.rFrameVolHttp = 0.
        self.rFrameVolHttps = 0.
        self.rFrameVolArp = 0.
        self.rFrameVolUdp = 0.   

    def addVolHttp(self,v):
        self.rSumVolHttp += v
        self.rSumVolTotal += v
        self.rFrameVolHttp += v
        self.rFrameVolTotal += v
        
    def addVolArp(self,v):
        self.rSumVolArp += v
        self.rSumVolTotal += v
        self.rFrameVolArp += v
        self.rFrameVolTotal += v
        
    def update( self ):
        #~ print("update")
        if time.time()-self.lastSend > self.rRefreshTimeSec:
            values = [ self.rSumVolTotal, self.rSumVolHttp, self.rSumVolHttps, self.rSumVolArp, self.rSumVolUdp,
                            self.rFrameVolTotal, self.rFrameVolHttp, self.rFrameVolHttps, self.rFrameVolArp, self.rFrameVolArp,
                        ]
            print("INF: Stater.update: sending")
            self.lastSend = time.time()
            self.sender.sendMessage("/global",values)
            
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
    aStater.startUpdateLoopInTheBackground()
    for i in range(50):
        aStater.addVolHttp(0.1)
        time.sleep(0.1)
    aStater.stopThread()