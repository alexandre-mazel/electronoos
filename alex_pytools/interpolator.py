# -*- coding: utf-8 -*-

import time

mode_normal = 0
mode_loop = 1
mode_pingpong = 2


class Interpolator:
    
    def __init__( self ):
        self.reset()
        
    def reset( self ):
        self.start_time = 0
        self.stop_time = 0
        self.duration = 0
        
        self.start_val = 0
        self.stop_val = 0
        self.val = 0
        
        self.is_running = False
        
        self.mode = mode_normal
        
        
    def set( self, stop_val, duration, start_val = None, mode = mode_normal ):
        self.stop_val = stop_val
        
        if start_val != None:
            self.start_val = start_val
        else:
            self.start_val = self.val
            
        self.duration = duration
        self.start_time = time.time()
        self.stop_time = self.start_time + duration
        
        self.is_running = True
            
        self.mode = mode
        
    def update( self ):
        
        verbose = 1
        #~ verbose = 0
        
        if not self.is_running: return
        
        if verbose:
            print( "DBG: Interpolator.update: is_running: %d, start_time: %.3f, stop_time: %.3f, duration: %.3f, start_val: %.3f" % 
                ( self.is_running, self.start_time, self.stop_time, self.duration, self.start_val ) )
            
        # compute the new value
        if self.mode == mode_normal:
            coef = (time.time() - self.start_time) / self.duration
            if coef > 1:
                coef = 1
                self.is_running = False
                
        self.val = self.start_val + coef * (self.stop_val-self.start_val)
        
    def get_val( self ):
        return self.val
# class Interpolator - end


class InterpolatorManager:
    def __init__( self, nbr_interpolator ):
        self.interpolators = []
        for i in range(nbr_interpolator):
            self.interpolators.append(Interpolator())
            
    def update( self ):
        for inter in self.interpolators:
            inter.update()
            
    def get( self,  num ):
        return self.interpolators[num]
             
# class InterpolatorManager - end    



def test_interpolator():
    nbr_interpolator = 100000
    im = InterpolatorManager(nbr_interpolator)
    
    if 1:
        for n in range( nbr_interpolator ):
            im.get(n).set( 1000, 5 )
    
    im.get(0).set( 1000, 5 )
    im.get(1).set( 1000, 5, 2000 )
    im.get(2).set( 1000, 5, mode = mode_loop )
    im.get(3).set( 1000, 5, mode = mode_pingpong )

        
    for i in range(15):
        print("time: %.3f" % time.time() )
        time_begin = time.time()
        im.update()
        update_duration = time.time() - time_begin
        print( "DBG: im.update takes %.4fs" % update_duration ) # ~ 0.05 for 100k, 0.01 when all are stopped
        print(im.get(0).get_val())
        time.sleep(1)
        
if __name__ == "__main__":
    test_interpolator()