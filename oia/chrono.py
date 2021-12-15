import time

class Chrono:
    
    def __init__( self ):
        self.reset()
        
    def reset( self ):
        self.start_time = None
        self.stop_time = None
        self.start_laps_time = None
        self.list_laps_time = []

    def start( self ):
        self.start_time = time.time()
        self.start_laps_time = self.start_time

    def stop( self ):
        if self.start_time == None:
            print("ERR: launch start before calling stop !")
            return
        self.start_new_laps()
        self.stop_time = time.time()
        
    def get_elapsed_time( self ):
        return self.stop_time - self.start_time
        
    def start_new_laps( self ):
        """
        will measure the time since start or since last call of this function
        """
        laps_time = time.time() - self.start_laps_time
        if laps_time >= 0.0001: # prevent case stopped just after start_new_laps
            self.list_laps_time.append(laps_time)
            self.start_laps_time = time.time()
        
    def get_all_laps_duration(self):
        return self.list_laps_time
        
    def get_average_time_per_laps( self ):
        sum = 0
        for t in self.list_laps_time:
            sum += t
        return sum/len(self.list_laps_time) # or simplier: get_elapsed_time()/len(self.list_laps_time)
        

def auto_test():
    c = Chrono()
    c.start()
    for i in range(4):
        time.sleep(1.)
        c.start_new_laps()
    c.stop()
    print(c.get_all_laps_duration())
    print(c.get_average_time_per_laps())
    assert(c.get_average_time_per_laps()>=1 and c.get_average_time_per_laps()<1.5)
    

if __name__ == "__main__":
    auto_test()
