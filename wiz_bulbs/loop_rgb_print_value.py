import asyncio

from pywizlight import wizlight, PilotBuilder, discovery # pip install pywizlight # NB: Requires Python version >=3.7.

import time

"""
INF: connecting to 192.168.0.110 ...
['__class__', '__del__', '__delattr__', '__dict__', '__dir__', '__doc__'
, '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '_
_hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__
module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '
__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__w
eakref__', '_async_close', '_async_send_register', '_cache_mac_from_bu
lb_config', '_ensure_connection', '_on_error', '_on_push', '_on_response', 'a
sync_close', 'bulbtype', 'diagnostics', 'extwhiteRange', 'fanSpeedRange', 'fa
nSwitch', 'fan_set_state', 'fan_turn_off', 'fan_turn_on', 'getBulbConfig', '
getExtendedWhiteRange', 'getFanSpeedRange', 'getMac', 'getModelConfig', '
getSupportedScenes', 'getUserConfig', 'getWhiteRange', 'get_bulbtype', 
'get_power', 'history', 'ip', 'last_push', 'lightSwitch', 'lock', 'loop', 'mac', 
'modelConfig', 'port', 'power_monitoring', 'protocol', 'push_callback', 
'push_cancel', 'push_running', 'reboot', 'register', 'reset', 'response_future',
 'response_method', 'send', 'send_no_async', 'set_discovery_callback', 
'set_ratio', 'set_speed', 'set_state', 'start_push', 'state', 'status', 'transport', 
'turn_off', 'turn_on', 'turn_on_noasync', 'updateState', 'whiteRange']
"""

async def print_bulb( b ):
    o = ""
    o += "getMac: %s\n" % await b.getMac()
    o += "getUserConfig: %s\n" % await b.getUserConfig()
    o += "bulbtype: %s\n" % b.bulbtype
    o += "state: %s\n" % b.state
    o += "status: %s\n" % b.status
    
    state = await b.updateState()
    o += "state2: %s\n" % b.state
    o += "state2.scene: %s\n" % state.get_scene()
    o += "state2.get_speed: %s\n" % state.get_speed()
    o += "state2.get_ratio: %s\n" % state.get_ratio()
    o += "state2.get_power: %s\n" % state.get_power()
    o += "state2.get_rgbw: %s\n" % state.get_rgbw()
    o += "state2.get_rgbww: %s\n" % state.get_rgbww()
    print(dir(state))
    
    print(o)


async def main():
    """Sample code to work with bulbs."""
    
            
    ip_bulb = "192.168.0.110"
    
    print( "INF: connecting to %s ..." % ip_bulb )
    
    light = wizlight(ip_bulb)
    
    print(dir(light))
    await print_bulb(light)
    
    # je voulais connaitre le rgb du candle light mais pas possible car c'est un mode interne
    while 0:

        # Get the current color temperature, RGB values
        state = await light.updateState()
        print("Color temp:", state.get_colortemp())
        red, green, blue = state.get_rgb()
        print(f"red: {red}, green: {green}, blue: {blue}")
        time.sleep(0.01)



loop = asyncio.get_event_loop()
loop.run_until_complete(main())