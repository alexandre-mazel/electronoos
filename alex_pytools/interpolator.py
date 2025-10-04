# -*- coding: utf-8 -*-

import math
import time

mode_normal = 0
mode_loop = 1
mode_pingpong = 2

interpolation_linear = 0
interpolation_sinus = 1

math.pi2 = math.pi / 2


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
        self.interpolation = interpolation_linear
        
        
    def set( self, stop_val, duration, start_val = None, mode = mode_normal, interpolation = interpolation_linear ):
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
        self.interpolation = interpolation
        
    def update( self ):
        
        verbose = 1
        verbose = 0
        
        if not self.is_running: return
        
        if verbose:
            print( "DBG: Interpolator.update: is_running: %d, mode: %d, interp: %d, start_time: %.3f, stop_time: %.3f, duration: %.3f, start_val: %.3f" % 
                ( self.is_running, self.mode, self.interpolation, self.start_time, self.stop_time, self.duration, self.start_val ) )
            
        # compute the new value
        if self.mode == mode_normal:
            coef = (time.time() - self.start_time) / self.duration
            if coef > 1:
                coef = 1
                self.is_running = False
        elif self.mode == mode_loop:
            coef = (time.time() - self.start_time) / self.duration
            coef = coef % 1 # modulo in float !
        elif self.mode == mode_pingpong:
            coef = (time.time() - self.start_time) / self.duration
            coef %= 2
            if verbose: print( "DBG: Interpolator.update: pingpong: coef intermediate: %.3f" % coef )
            if coef > 1:
                # reverse mode
                coef = 2-coef
        
        if self.interpolation != interpolation_sinus:
            self.val = self.start_val + coef * (self.stop_val-self.start_val)
        else:
            self.val = self.start_val + math.sin(coef*math.pi2) * (self.stop_val-self.start_val)
        
        
        if verbose: print( "DBG: Interpolator.update: coef: %.3f, val: %3f" % ( coef, self.val ) )
        
    def get_val( self ):
        return self.val
        
    def update_get( self ):
        """
        Update and get value
        """
        self.update()
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

def draw_interpolator():
    import matplotlib.pyplot as plt

    # Generate data
    t = 0
    nbr_interpolator = 6
    im = InterpolatorManager( nbr_interpolator )
    im.get(0).set( 1000, 1 )
    im.get(1).set( 1000, 1, mode = mode_loop )
    im.get(2).set( 1000, 1, mode = mode_pingpong )
    im.get(3).set( 1000, 1, interpolation = interpolation_sinus )
    im.get(4).set( 1000, 1, interpolation = interpolation_sinus, mode = mode_loop )
    im.get(5).set( 1000, 1, interpolation = interpolation_sinus, mode = mode_pingpong )
    values = []
    for i in range( nbr_interpolator ):
        values.append( [] )
    
    ts  = []
    for t in range( 2000 ):
        ts.append(t/1000)
        im.update()
        for i in range( nbr_interpolator ):
            values[i].append( im.get(i).get_val() )
        time.sleep( 1/1000 )

    # Plot
    plt.figure(figsize=(10,6))
    plt.plot(ts, values[0], label="normal")
    plt.plot(ts, values[1], label="loop")
    plt.plot(ts, values[2], label="pingpong")
    plt.plot(ts, values[3], label="sinus normal")
    plt.plot(ts, values[4], label="sinus loop")
    plt.plot(ts, values[5], label="sinus pingpong")

    # Limit y range
    #~ plt.ylim(-10, 10)

    plt.title("Interpolator")
    plt.xlabel("t")
    plt.ylabel("val")
    plt.legend()
    plt.grid(True)
    plt.show()


def test_interpolator():
    nbr_interpolator = 100000
    im = InterpolatorManager(nbr_interpolator)
    
    if 0:
        for n in range( nbr_interpolator ):
            im.get(n).set( 1000, 5 )
    
    im.get(0).set( 1000, 5 )
    im.get(1).set( 1000, 5, interpolation = interpolation_sinus )
    im.get(10).set( 1000, 5, 2000 )
    im.get(20).set( 1000, 5, mode = mode_loop )
    im.get(30).set( 1000, 5, mode = mode_pingpong )

        
    for i in range(15):
        print("time: %.3f" % time.time() )
        time_begin = time.time()
        im.update()
        update_duration = time.time() - time_begin
        print( "DBG: im.update takes %.4fs" % update_duration )
        """ 
        Duration:
        mstab7:  ~ 0.05 for 100k running, 0.01 when all are stopped
        """
        
        print("interpolator0: val: ", im.get(0).get_val())
        time.sleep(1)
        
if __name__ == "__main__":
    draw_interpolator()
    #~ test_interpolator()