
import tinytuya # pip install tinytuya

d = tinytuya.BulbDevice("DEVICE_ID", "192.168.0.80", "LOCAL_KEY")
d.set_version(3.3)   # Tuya protocol version

# Turn on bulb
d.turn_on()

# Set brightness (0-255)
d.set_brightness(128)

# Set color (HSV values)
d.set_colour(255, 0, 255)