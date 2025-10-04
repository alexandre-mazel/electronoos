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
    im = interpolator.Interpolator( nbr_chan )




if __name__ == "__main__":
    dmx_device = None
    
    #~ dmx_device = init_dmx(492+16)
    prog_ccc(dmx_device, nbr_chan)
