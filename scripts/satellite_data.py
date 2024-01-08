from pystac_client import Client # pip install pystac_client
from odc.stac import load # pip install odc-stac
import time

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# simple plt sample:
#~ plt.plot([1, 2, 3, 4])
#~ plt.ylabel('some numbers')
#~ plt.show()

#~ fig = Figure()
#~ canvas = fig.canvas
#~ ax = fig.gca()
#~ canvas.draw()

client = Client.open("https://earth-search.aws.element84.com/v1")
collection = "sentinel-2-l2a"
tas_bbox = [146.5,-43.6,146.7,-43.4]
search = client.search(collections=[collection],bbox=tas_bbox,datetime="2023-12")
data = load(search.items(),bbox=tas_bbox,groupby="solar_day",chunks={})
object=data[["red","green","blue"]].isel(time=2).to_array().plot
ret = object.imshow(robust=True)

plt.show() # cf satelitte_data_output.png for example of output

#~ print("ret: " + str(ret))
#~ import matplotlib
#~ matplotlib.pyplot.draw()
#~ plt.waitforbuttonpress(timeout=-1)
#~ ret.draw()
#~ ret.draw(renderer=?)

#~ ret.draw_image()



if 0:
    import numpy as np
    from PIL import Image, ImageTk
    #~ image1 = Image.fromarray(np.uint8( ret.get_cmap()(ret.get_array())*255))
    image1 = Image.fromarray(ret)
    image1.save("/tmp/satellite.jpg")
    im = ImageTk.PhotoImage('RGB', image1.size)
    im.paste(image1)
    test = canvas.create_image(0, 0, image=im)
    mainloop()

print("wait for user to see")
time.sleep(3)