import asyncio

from pywizlight import wizlight, PilotBuilder, discovery # pip install pywizlight # NB: Requires Python version >=3.7.

async def main():
    """Sample code to work with bulbs."""
    
    if 0:
        # Discover all bulbs in the network via broadcast datagram (UDP)
        # function takes the discovery object and returns a list of wizlight objects.
        print( "INF: discovering from broadcast...")
        bulbs = await discovery.discover_lights(broadcast_space="192.168.0.255")
        
        print( "INF: Bulb found: nb: %s" % len(bulbs))
        # Print the IP address of the bulb on index 0
        print(f"Bulb IP address: {bulbs[0].ip}")

        # Iterate over all returned bulbs
        for bulb in bulbs:
            print(bulb.__dict__)
            # Turn off all available bulbs
            await bulb.turn_on()
            time.sleep(1)
            await bulb.turn_off()
            
    ip_bulb = "192.168.0.22"
    
    print( "INF: connecting to %s" % ip_bulb )

    # Set up a standard light
    light = wizlight(ip_bulb)
    # Set up the light with a custom port
    #light = wizlight("your bulb's IP address", port=12345)

    # The following calls need to be done inside an asyncio coroutine
    # to run them from normal synchronous code, you can wrap them with
    # asyncio.run(..).

    # Turn the light on into "rhythm mode"
    await light.turn_on(PilotBuilder())
    
    # Set bulb brightness
    await light.turn_on(PilotBuilder(brightness = 255))

    # Set bulb brightness (with async timeout)
    timeout = 10
    await asyncio.wait_for(light.turn_on(PilotBuilder(brightness = 255)), timeout)

    # Set bulb to warm white
    await light.turn_on(PilotBuilder(warm_white = 255))

    # Set RGB values
    # red to 0 = 0%, green to 128 = 50%, blue to 255 = 100%
    await light.turn_on(PilotBuilder(rgb = (0, 128, 255)))

    # Get the current color temperature, RGB values
    state = await light.updateState()
    print(state.get_colortemp())
    red, green, blue = state.get_rgb()
    print(f"red {red}, green {green}, blue {blue}")

    # Start a scene
    await light.turn_on(PilotBuilder(scene = 4)) # party

    # Get the name of the current scene
    state = await light.updateState()
    print(state.get_scene())

    # Get the features of the bulb
    bulb_type = await light.get_bulbtype()
    print( "INF: features:")
    print("- Brightness:", bulb_type.features.brightness) # returns True if brightness is supported
    print("- Color:", bulb_type.features.color) # returns True if color is supported
    print("- Color temp:", bulb_type.features.color_tmp) # returns True if color temperatures are supported
    print("- Effect:", bulb_type.features.effect) # returns True if effects are supported
    print("- K_max:", bulb_type.kelvin_range.max) # returns max kelvin in INT
    print("- K_min:", bulb_type.kelvin_range.min) # returns min kelvin in INT
    print("- type_name:", bulb_type.name) # returns the module name of the bulb

    # Turn the light off
    await light.turn_off()

    # Do operations on multiple lights in parallel
    #bulb1 = wizlight("<your bulb1 ip>")
    #bulb2 = wizlight("<your bulb2 ip>")
    # --- DEPRECATED in 3.10 see [#140](https://github.com/sbidy/pywizlight/issues/140)
    # await asyncio.gather(bulb1.turn_on(PilotBuilder(brightness = 255)),
    #    bulb2.turn_on(PilotBuilder(warm_white = 255)))
    # --- For >3.10 await asyncio.gather() from another coroutine
    # async def turn_bulbs_on(bulb1, bulb2):
    #    await asyncio.gather(bulb1.turn_on(PilotBuilder(warm_white=255)), bulb2.turn_on(PilotBuilder(warm_white=255)))
    #  def main:
    #    asyncio.run(async turn_bulbs_on(bulb1, bulb2))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())