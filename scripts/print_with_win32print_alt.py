import win32print
import win32ui
from PIL import Image, ImageWin

#
# Constants for GetDeviceCaps
#
#
# HORZRES / VERTRES = printable area
#
HORZRES = 8
VERTRES = 10
#
# LOGPIXELS = dots per inch
#
LOGPIXELSX = 88
LOGPIXELSY = 90
#
# PHYSICALWIDTH/HEIGHT = total area
#
PHYSICALWIDTH = 110
PHYSICALHEIGHT = 111
#
# PHYSICALOFFSETX/Y = left / top margin
#
PHYSICALOFFSETX = 112
PHYSICALOFFSETY = 113

printer_name = win32print.GetDefaultPrinter()
print("printer_name: " + printer_name)

#
# You can only write a Device-independent bitmap
#  directly to a Windows device context; therefore
#  we need (for ease) to use the Python Imaging
#  Library to manipulate the image.
#
# Create a device context from a named printer
#  and assess the printable size of the paper.
#


if 0:
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
    PRINTER_DEFAULTS = {"DesiredAccess":win32print.PRINTER_ALL_ACCESS}
    temprint=printers[1][2]
    temprint=printer_name
    print("printers: %s" % str(printers))
    print("temprint: %s" % temprint)
    handle = win32print.OpenPrinter(temprint, PRINTER_DEFAULTS)
    level = 2
    handle = win32print.OpenPrinter(temprint, PRINTER_DEFAULTS)
    attributes = win32print.GetPrinter(handle, level)
    attributes['pDevMode'].PaperWidth = 600  
    attributes['pDevMode'].PaperLength = 30  
    attributes['pDevMode'].PaperSize =0 


hDC = win32ui.CreateDC ()
if 1:
    hDC.CreatePrinterDC (printer_name)
else:
    hprinter = win32print.OpenPrinter(printer)
devmode = win32print.GetPrinter(hprinter, 2)["pDevMode"]
devmode.PaperSize = 20
devmode.Orientation = 2

printable_area = hDC.GetDeviceCaps (HORZRES), hDC.GetDeviceCaps (VERTRES)
printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)
printer_margins = hDC.GetDeviceCaps (PHYSICALOFFSETX), hDC.GetDeviceCaps (PHYSICALOFFSETY)

print("printer_size: %s" % str(printer_size))
print("printable_area: %s" % str(printable_area))
print("printer_margins: %s" % str(printer_margins))

printer_size = (printer_size[0],1795)
printable_area = (printer_size[0]-2*printer_margins[0],printer_size[1]-2*printer_margins[1])
print("apres modification")
print("printer_size: %s" % str(printer_size))
print("printable_area: %s" % str(printable_area))

#
# Open the image, rotate it if it's wider than
#  it is high, and work out how much to multiply
#  each pixel by to get it as big as possible on
#  the page without distorting.
#
file_name = "c:/users/alexa/downloads/stickers.jpg"
file_name = "C:/Users/alexa/perso/docs/2023-10_cdl_photosbooths/stickers.jpg"

bmp = Image.open( file_name )

print("bmp.size (1): %s" % str(bmp.size))
realBmpSize = (bmp.size[0],bmp.size[1])

if bmp.size[0] < bmp.size[1]:
    realBmpSize = (bmp.size[1],bmp.size[0])
    bmp = bmp.rotate(90)
  
print("bmp.size (2): %s" % str(bmp.size))
print("realBmpSize: %s" % str(realBmpSize))


ratios = [1.0 * printable_area[0] / realBmpSize[0], 1.0 * printable_area[1] / realBmpSize[1]]
scale = min (ratios)

#
# Start the print job, and draw the bitmap to
#  the printer device at the scaled size.
#
exit(0)

hDC.StartDoc (file_name)
hDC.StartPage ()

dib = ImageWin.Dib (bmp)
scaled_width, scaled_height = [int (scale * i) for i in realBmpSize]
x1 = int ((printer_size[0] - scaled_width) / 2)
y1 = int ((printer_size[1] - scaled_height) / 2)
x2 = x1 + scaled_width
y2 = y1 + scaled_height
print("x1: %s, y1: %s, x2: %s, y2: %s" % (x1,y1,x2,y2))
dib.draw (hDC.GetHandleOutput (), (x1, y1, x2, y2))

hDC.EndPage ()
hDC.EndDoc ()
hDC.DeleteDC ()