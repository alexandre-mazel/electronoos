import win32print
import win32ui
from PIL import Image, ImageWin

PHYSICALWIDTH = 110
PHYSICALHEIGHT = 111

printer_name = win32print.GetDefaultPrinter ()
print("printer_name: " + printer_name)

file_name = "new.jpg"

hDC = win32ui.CreateDC ()
hDC.CreatePrinterDC (printer_name)
printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)

print("printer_size: " + str(printer_size))

file_name = "c:/users/alexa/downloads/stickers.jpg"

bmp = Image.open (file_name)
#~ if bmp.size[0] < bmp.size[1]:
  #~ bmp = bmp.rotate (90)

hDC.StartDoc (file_name)
hDC.StartPage ()

dib = ImageWin.Dib (bmp)
dib.draw (hDC.GetHandleOutput (), (0,0,printer_size[0]//2,printer_size[1]//2))

hDC.EndPage ()
hDC.EndDoc ()
hDC.DeleteDC ()