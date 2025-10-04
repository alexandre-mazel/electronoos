# -*- coding: utf-8 -*-

from ccc import *

import sys
sys.path.append("../alex_pytools/")
import interpolator

"""
Alternate dmx light intensity for Oscillation

# 1. Install python
https://www.python.org/downloads/
(or brew)

# 2. Install libraries:
pip3 install serial pyserial numpy 

"Copyright" 2025 Alexandre Mazel
"""

def prog_ccc( dm, nbr_chan ):
    im = interpolator.InterpolatorManager( nbr_chan )
    
    # update and set values:
    #~ dmxal.set_verbose( True )
    print("looping...")
    while 1:
        print(".", end="")
        im.update()
        for i in range( 1, nbr_chan ):
            dm.set_data(i,im.get(i).get_val(), auto_send = False)
        dm.send()
        time.sleep(0.1)
        




if __name__ == "__main__":
    dmx_device = None
    nbr_chan = 492+16 # how much did we use ?
    if 1:
        dmx_device = init_dmx(nbr_chan)
        #~ dmx_device.set_optimised( 1 )
    
    prog_ccc(dmx_device, nbr_chan)
