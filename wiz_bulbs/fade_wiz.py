import asyncio

from pywizlight import wizlight, PilotBuilder, discovery # pip install pywizlight # NB: Requires Python version >=3.7.

import time

# ramp between 0 and 1 but nonlinear (avec un ventre haut)
# speed at first then slow
def nonlinear_ramp0(coef: int ):
    gamma = 2.4  # Exposant, adjusted so the value 0.5 gives ~0.25
    output = pow(coef, gamma)
    #~ return output # slow at first, then speed
    # symetrie par rapport a x=y
    if output == 0:
        return 0
    output = coef + (coef-output)
    if output > 1.:
        return 1.
    return output
    
def nonlinear_ramp(coef: int ):
    # decoupe en 3 parties:
    # premiere partie tres rapide (jusqu'a p1)
    # deuxieme partie lineaire (jusqu'a p2)
    # troisieme partie tres lente
    step1 = 0.3
    step2 = 0.5 # to disable it put less than step1
    
    p1 = 0.5
    p2 = 0.8
    
    if coef <= step1:
        c = coef/step1
        output = p1 * c
    elif coef <= step2:
        c = (coef-step1)/(step2-step1)
        output = p1 * (1-c)+ p2 * c
    else:
        c = (coef-step2)/(1-step2)
        output = p2 * (1-c)+ 1. * c
    return output
        
if 0:
    for i in range(0,100):
        coef = i / 100.
        print( "%.3f => %.3f" % (coef, nonlinear_ramp(coef) ))
    exit(1)

async def fade_wiz(col1, col2, duration):
    """Sample code to work with bulbs."""
    
    print( "INF: fade_wiz: starting...")
    
    #~ ips_bulb = ["192.168.0.110","192.168.0.111","192.168.0.112"]
    ips_bulb = ["192.168.0.110","192.168.0.112"]
    ips_bulb = ["192.168.0.112"]
    
    bulbs = []
    
    for ip in ips_bulb:
        print( "INF: fade_wiz: connecting to %s ..." % ip )
        bulbs.append(wizlight(ip))
        

    time_begin = time.time()
    mute = 0
    while time.time() - time_begin <=  duration:
        t = time.time() - time_begin
        col = [0,0,0,0,0]
        coef0 = t / duration
        coef = coef0
        #~ coef = nonlinear_ramp( coef0 )
        coef_presque = (duration - 0.2) / duration # presque a fond # 0.2 is a rough approx of the time to send command
        if coef > coef_presque:
            print("coef0: %.3f, coef: %.3f, presque: %.3f" % (coef0, coef, coef_presque) )
            coef = 1
        for i in range(5):
            col[i] = round(col_1[i] * (1-coef) + col_2[i] * coef)
            if col[i] < 0:
                col[i] = 0
        print( "t: %.4f coef0: %.3f, coef: %.3f, r g b ww cw: %s" % (t, coef0, coef, str(col)) )
        
        for bulb in bulbs:
            if mute:
                await bulb.turn_off()
            else:
                #~ await bulb.turn_on(PilotBuilder(brightness = bright,rgb = (r, g, b))
                #~ await bulb.turn_on(PilotBuilder(rgbw = (r, g, b,bright)))
                #~ await bulb.turn_on(PilotBuilder(rgbww = (0,0,0,113,113)))
                r, g, b,ww,cw = col
                await bulb.turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww)))
    
        time.sleep(0.001)

loop = asyncio.get_event_loop()

# reglage pour eclairage oeuvre.

duration = 10 # in sec
col_1 = (0, 0, 0, 255, 255)
col_2 = (0, 5, 128, 0, 0)

loop.run_until_complete(fade_wiz(col_1,col_2,duration))

duration = 5 # in sec
col_1 = (0, 5, 35, 0, 0)
col_2 = (0, 5, 7, 0, 0)
loop.run_until_complete(fade_wiz(col_1,col_2,duration))