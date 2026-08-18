import paho.mqtt.client as mqtt # pip install paho-mqtt

BROKER = "192.168.0.80"  # IP of your MQTT broker
# a priori le broker doit tourner sur un ordi local
TOPIC = "cmnd/lepro_bulb1"

# Connect
client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# Turn ON
client.publish(f"{TOPIC}/POWER", "ON")

# Set brightness to 70%
client.publish(f"{TOPIC}/Dimmer", "70")

# Set color to blue
client.publish(f"{TOPIC}/Color", "0000FF")

# Disconnect
client.disconnect()