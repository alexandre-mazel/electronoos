# -*- coding: utf-8 -*-

import math
import noise
import random
import time

mode_normal = 0
mode_loop = 1
mode_pingpong = 2
mode_random = 3
mode_perlin = 4

interpolation_linear = 0
interpolation_sinus = 1          # accelerate slowly, decelerate slowly
interpolation_sinus2 = 1          # accelerate very slowly, decelerate very slowly
interpolation_halfsinus = 3   # accelerate quickly, decelerate slowly

math.pi2 = math.pi / 2

def precise_sleep(duration_sec):
    target = time.perf_counter() + duration_sec
    while time.perf_counter() < target:
        pass


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
        reverse = 0
        if self.duration < 0.00001:
            coef = 1
            self.is_running = False #even for ping pong
        else:
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
                    reverse = 1
            elif self.mode == mode_random:
                coef = random.random()
            elif self.mode == mode_perlin:
                coef = ( noise.getSimplexNoise( (time.time() - self.start_time)/ self.duration, y = time.time() ) + 1 ) / 2 # y = time.time() to add a variety to each random
        
        if self.interpolation == interpolation_linear:
            self.val = self.start_val + coef * (self.stop_val-self.start_val)
            
        elif self.interpolation == interpolation_sinus:
            if not reverse:
                self.val = self.start_val + (math.sin(coef*math.pi-math.pi2)+1)/2 * (self.stop_val-self.start_val)
            else:
                self.val = self.start_val + ( 1 - math.sin((1-coef)*math.pi-math.pi2) )/2 * (self.stop_val-self.start_val)
                
        elif self.interpolation == interpolation_sinus2:
            if not reverse:
                self.val = self.start_val + ((math.sin(coef*math.pi-math.pi2)+1)/2)**4 * (self.stop_val-self.start_val)
            else:
                self.val = self.start_val + (( 1 - math.sin((1-coef)*math.pi-math.pi2) )/2)**4 * (self.stop_val-self.start_val)
                
                
        elif self.interpolation == interpolation_halfsinus:
            if not reverse:
                self.val = self.start_val + math.sin(coef*math.pi2) * (self.stop_val-self.start_val)
            else:
                self.val = self.start_val + ( 1 - math.sin((1-coef)*math.pi2) ) * (self.stop_val-self.start_val)
        
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
        
    def is_all_finished( self ):
        for interp in self.interpolators:
            if interp.is_running:
                return False
        return True
             
# class InterpolatorManager - end

def draw_interpolator():
    import numpy as np
    import matplotlib.pyplot as plt

    # Generate data
    t = 0
    n = 0
    nbr_interpolator = 14
    im = InterpolatorManager( nbr_interpolator )
    im.get(n).set( 1000, 1 ); n += 1
    im.get(n).set( 1000, 1, mode = mode_loop ); n += 1
    im.get(n).set( 1000, 1, mode = mode_pingpong ); n += 1
    im.get(n).set( 1000, 1, mode = mode_random ); n += 1
    im.get(n).set( 1000, 1, mode = mode_perlin ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_sinus ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_sinus, mode = mode_loop ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_sinus, mode = mode_pingpong ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_sinus2 ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_sinus2, mode = mode_loop ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_sinus2, mode = mode_pingpong ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_halfsinus ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_halfsinus, mode = mode_loop ); n += 1
    im.get(n).set( 1000, 1, interpolation = interpolation_halfsinus, mode = mode_pingpong ); n += 1
    values = []
    for i in range( nbr_interpolator ):
        values.append( [] )
    
    # on aurait aimer faire du temps réel, mais on est un peu loin de ca.
    ts  = []
    for t in range( 4000 ):
        ts.append(t/1000)
        im.update()
        for i in range( nbr_interpolator ):
            values[i].append( im.get(i).get_val() - 2000 * i )
        #~ time.sleep( 1/1000 )
        #~ time.sleep( 0.000001 ) # le sleep est tres lent et peu précis
        if t == 3000:
            # send another command plus rapide
            n = 0
            im.get(n).set( 1000, 0.25, start_val = 0, mode = mode_normal ); n += 1
            im.get(n).set( 1000, 0.25, start_val = 0, mode = mode_loop ); n += 1
            im.get(n).set( 1000, 0.25, start_val = 0, mode = mode_pingpong ); n += 1
            im.get(n).set( 1000, 0.25, start_val = 0, mode = mode_random ); n += 1
            im.get(n).set( 1000, 0.25, start_val = 0, mode = mode_perlin )
            
        precise_sleep( 1/1000 )

    # Plot
    n = 0
    plt.figure(figsize=(10,6))
    plt.plot(ts, values[n], label="normal"); n +=1
    plt.plot(ts, values[n], label="loop"); n +=1
    plt.plot(ts, values[n], label="pingpong"); n +=1
    plt.plot(ts, values[n], label="random"); n +=1
    plt.plot(ts, values[n], label="perlin"); n +=1
    plt.plot(ts, values[n], label="sinus normal"); n +=1
    plt.plot(ts, values[n], label="sinus loop"); n +=1
    plt.plot(ts, values[n], label="sinus pingpong"); n +=1
    plt.plot(ts, values[n], label="sinus2 normal"); n +=1
    plt.plot(ts, values[n], label="sinus2 loop"); n +=1
    plt.plot(ts, values[n], label="sinus2 pingpong"); n +=1
    plt.plot(ts, values[n], label="halfsinus normal"); n +=1
    plt.plot(ts, values[n], label="halfsinus loop"); n +=1
    plt.plot(ts, values[n], label="halfsinus pingpong"); n +=1

    # Limit y range
    #~ plt.ylim(-10, 10)

    plt.title("Interpolator")
    plt.xlabel("t")
    plt.ylabel("val")
    
    plt.yticks(np.arange(-2000*nbr_interpolator, 2000, 1000)) # show horizontal grid bar
    #~ plt.gca().get_yaxis().set_visible(False) # hide y axis
    plt.gca().set_yticklabels([]) # hide the labels but keep the ticks/grid
    
    #~ plt.legend()
    plt.legend(loc="upper right")
    plt.tight_layout(pad=0) # fonctionne pas sur le premier?
    plt.grid(True)
    
    fn = 'datas/interpolator.png'
    plt.savefig(fn, dpi=100)
    
    plt.show()



def test_interpolator():
    nbr_interpolator = 100000
    im = InterpolatorManager(nbr_interpolator)
    
    if 1:
        for n in range( nbr_interpolator ):
            im.get(n).set( 1000, 5, interpolation = interpolation_sinus2 )
    
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
        mstab7:  ~ 0.05 for 100k running linear, 0.08 for 100k running sinus, 0.085 for 100k running sinus2, 0.01 when all are stopped
        """
        
        print("interpolator0: val: ", im.get(0).get_val())
        time.sleep(1)
        
if __name__ == "__main__":
    draw_interpolator()
    #~ test_interpolator()