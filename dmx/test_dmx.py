from dmx import DMX # git clone https://github.com/monzelr/dmx.git, cd dmx, pip install .
# Tested on Windows 10, amd64, Python 3.8
# Should also work on Linux, MacOS and on AARCH64 devices (ARM devices like Raspberry PI).
# Tested by Alexandre: 

import time

print( "Running Dmx...")
dmx = DMX( num_of_channels = 4 )
print(dir(dmx))
print("INF: dmx.is_connected(): ", dmx.is_connected() )
print("INF: dmx.num_of_channels: ", dmx.num_of_channels )

print(dir(dmx.device))
print("INF: dmx.device.name: ", dmx.device.name )
print("INF: dmx.device.pid: ", dmx.device.pid )
print("INF: dmx.device.product: ", dmx.device.product )
print("INF: dmx.device.manufacturer: ", dmx.device.manufacturer )
print("INF: dmx.device.serial_number: ", dmx.device.serial_number )

print("INF: dmx: starting" )

dmx.set_data(1, 0)
dmx.set_data(2, 0)
dmx.set_data(3, 0)
dmx.set_data(4, 0)

while True:
    print(".")
    for i in range(0, 255, 5):
        dmx.set_data(1, i, auto_send=False)
        dmx.set_data(2, i, auto_send=False)
        dmx.set_data(3, i, auto_send=False)
        dmx.set_data(4, i)
        time.sleep(0.01)

    for i in range(255, 0, -5):
        dmx.set_data(1, i, auto_send=False)
        dmx.set_data(2, i, auto_send=False)
        dmx.set_data(3, i, auto_send=False)
        dmx.set_data(4, i)
        time.sleep(0.01)