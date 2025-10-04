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

async def fade_wiz(col1, col2, duration, just_one_call = False):
    """
    Fade between two colors: col1 => col2
    colors are a tuple: r, g, b, ww, cw, brightness
    """
    
    print( "INF: fade_wiz: starting...")
    
    #~ ips_bulb = ["192.168.0.110","192.168.0.111","192.168.0.112", "192.168.0.113", "192.168.0.114", "192.168.0.120", "192.168.0.121"]
    #~ ips_bulb = ["192.168.0.110","192.168.0.112"]
    #~ ips_bulb = ["192.168.0.112"]
    #~ ips_bulb = ["192.168.0.110","192.168.0.121"]
    ips_bulb = ["192.168.0.110"]
    ips_bulb = ["192.168.9.223"]
    
    bulbs = []
    
    for ip in ips_bulb:
        print( "INF: fade_wiz: connecting to %s ..." % ip )
        bulbs.append(wizlight(ip))
        

    time_begin = time.time()
    mute = 0
    cpt = 0
    while time.time() - time_begin <=  duration:
        t = time.time() - time_begin
        col = [0,0,0, 0,0, 0]
        coef0 = t / duration
        coef = coef0
        #~ coef = nonlinear_ramp( coef0 )
        coef_presque = (duration - 0.2) / duration # presque a fond # 0.2 is a rough approx of the time to send command
        if coef > coef_presque or just_one_call:
            print("coef0: %.3f, coef: %.3f, presque: %.3f" % (coef0, coef, coef_presque) )
            coef = 1
        for i in range(6):
            col[i] = round(col1[i] * (1-coef) + col2[i] * coef)
            if col[i] < 0:
                col[i] = 0
        print( "cpt: %d, t: %.4f coef0: %.3f, coef: %.3f, r g b ww cw bright: %s" % ( cpt, t, coef0, coef, str(col) ) )
        
        r, g, b,ww,cw, bright = col
        
        if r == 0 and g == 0 and b == 0 and ww == 0 and cw == 0 and bright == 0:
            print( "INF: muting" )
            mute = 1
        else:
            mute = 0
        
        if 0:
            
            for i,bulb in enumerate(bulbs):
                if mute:
                    await bulb.turn_off()
                else:
                    #~ await bulb.turn_on(PilotBuilder(brightness = bright,rgb = (r, g, b))
                    #~ await bulb.turn_on(PilotBuilder(rgbw = (r, g, b,bright)))
                    #~ await bulb.turn_on(PilotBuilder(rgbww = (0,0,0,113,113)))
                    
                    # on a a peu pres 233ms par appel
                    # await just the last one (ca fonctionne pas)
                    if i == len(bulbs)-1:
                        await bulb.turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright))
                    else:
                        bulb.turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright))
        else:
            # on gagne grave: ca prend 260ms pour 3 appels (270ms pour 7 appels)
            if mute == 0:
                await asyncio.gather(
                    bulbs[0].turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright)),
                    #~ bulbs[1].turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright)),
                    #~ bulbs[2].turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright)),
                    #~ bulbs[3].turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright)),
                    #~ bulbs[4].turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright)),
                    #~ bulbs[5].turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright)),
                    #~ bulbs[6].turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww),brightness=bright)),
                )
            else:
                await asyncio.gather(
                    bulbs[0].turn_off(),
                    #~ bulbs[1].turn_off(),
                    #~ bulbs[2].turn_off(),
                    #~ bulbs[3].turn_off(),
                    #~ bulbs[4].turn_off(),
                    #~ bulbs[5].turn_off(),
                    #~ bulbs[6].turn_off(),
                )
                if 0:
                    print( "INF: ultraforce muting" )
                    await bulbs[0].turn_off()
                    
        cpt += 1
        
        if just_one_call:
            break
            
        time.sleep(0.01)
    
    print( "time per call: %.2fs" % ((time.time() - time_begin) / cpt) )
    
# fade_wiz - end

loop = asyncio.get_event_loop()

if 0:
    # reglage pour eclairage oeuvre.

    duration = 10 # in sec
    col_1 = (0, 0, 0, 255, 255)
    col_2 = (0, 5, 128, 0, 0)

    loop.run_until_complete(fade_wiz(col_1,col_2,duration))

    duration = 5 # in sec
    col_1 = (0, 5, 35, 0, 0)
    col_2 = (0, 5, 7, 0, 0)
    loop.run_until_complete(fade_wiz(col_1,col_2,duration))
    
if 0:
    # reglage pour fade dans les bleus.

    duration = 10 # in sec
    col_1 = (0, 20, 255, 0, 0, 0)
    col_2 = (0, 20, 255, 0, 0, 255)
    loop.run_until_complete(fade_wiz(col_1,col_2,duration))
    
if 0:
    # reglage pour fade red vers bleu

    duration = 10 # in sec
    col_1 = (0, 0, 255, 0, 0, 0)
    col_2 = (255, 0, 0, 0, 0, 0)
    loop.run_until_complete(fade_wiz(col_1,col_2,duration))

    col_1 = (0, 0, 255, 0, 0, 255)
    col_2 = (0, 0, 0, 0, 0, 0)    
    loop.run_until_complete(fade_wiz(col_1,col_2,duration))
    loop.run_until_complete(fade_wiz(col_2,col_1,duration))
    
if 0:
    duration = 10 # in sec
    col_1 = (10, 20, 30, 40, 200)
    col_2 = (10, 20, 30, 40, 200)

    loop.run_until_complete(fade_wiz(col_1,col_2,duration))
    
if 0:
    # reglage pour eclairage oeuvre #2: avec brightness bien gere.
    duration = 20.6 # in sec
    col_1 = (0,0,0,255,255,255)
    #~ col_1 = (0, 5, 60,0,0,40)
    col_2 = (0, 5, 20, 90,90,90)

    #~ loop.run_until_complete(fade_wiz(col_1,col_2,duration))
    
    duration2 = 30
    col_3 = (0, 5, 29,6,6,44)
    #~ loop.run_until_complete(fade_wiz(col_2,col_3,duration2))
    
    duration3 = 2.4
    col_4 = (0, 5, 30,0,0,40)
    #~ loop.run_until_complete(fade_wiz(col_3,col_4,duration3))


    # a voir si on fait le retoure plus rapide ou pas, avec un palier encore juste tres pres du full bleu qui est trop rapide,
    # [0, 5, 10, 94, 94, 94]

    # remontee
    loop.run_until_complete(fade_wiz(col_4,col_4,5))  # pause sur la couleur
    loop.run_until_complete(fade_wiz(col_4,col_3,duration3/2))
    loop.run_until_complete(fade_wiz(col_3,col_2,duration2/3))
    loop.run_until_complete(fade_wiz(col_2,col_1,duration/3))
    
if 0: 
    # reglage rapide de couleur
    col = (0, 5, 30,0,0,40)
    loop.run_until_complete(fade_wiz(col,col,1))
    
    
if 1: 
    # reglage rapide de communication
    col_1 = (0,0,0,255,255,255)
    col_2 = (0,255,0,0,0,255)
    col_3 = (0,0,255,0,0,255)
    col_4 = (0,0,255,0,0,0)
    col_off = (0,0,0,0,0,0)
    loop.run_until_complete(fade_wiz(col_1,col_2,3))
    loop.run_until_complete(fade_wiz(col_2,col_3,3))
    loop.run_until_complete(fade_wiz(col_3,col_4,7))
    # essaye de forcer la lampe a s'eteindre
    loop.run_until_complete(fade_wiz(col_4,col_off,2)) # force to call it
    loop.run_until_complete(fade_wiz(col_off,col_off,1,just_one_call=True))

    