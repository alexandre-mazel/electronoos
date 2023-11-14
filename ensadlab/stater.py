"""
Yet another statistics tools.
Store statistics and send them to osc viewer
"""
import sys
sys.path.append("../osc_viewer")
import send_osc
import time

class Stater:
    
    def __init__( self, rPeriodSec = 1., viewer_ip="127.0.0.1" ):
        self.period = rPeriodSec
        self.viewer_ip = viewer_ip
        self.sender = send_osc.Sender()
        self.sender.connect(viewer_ip)
        
        self.reset()
        
    def reset( self ):
        print("INF: Stater.reset")
        self.rSumVolTotal = 0.
        self.rSumVolHttp = 0.
        self.rSumVolHttps = 0.
        self.rSumVolArp = 0.
        self.rSumVolUdp = 0.
        self.startNewFrame()
        self.lastSend = time.time()-10000 # time last send in epoch

        
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
        
    def update( self ):
        if time.time()-self.lastSend > self.period:
            values = [ self.rSumVolTotal, self.rSumVolHttp, self.rSumVolHttps, self.rSumVolArp, self.rSumVolUdp,
                            self.rFrameVolTotal, self.rFrameVolHttp, self.rFrameVolHttps, self.rFrameVolArp, self.rFrameVolArp,
                        ]
            print("INF: Stater.update: sending")
            self.sender.sendMessage("/global",values)
            self.lastSend = time.time()
            self.startNewFrame()
        
        
        
stater = Stater()

if __name__ == "__main__":
    for i in range(50):
        stater.addVolHttp(0.1)
        stater.update()
        time.sleep(0.1)