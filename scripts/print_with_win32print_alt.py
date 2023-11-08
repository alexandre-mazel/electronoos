import win32print
import win32ui
from PIL import Image, ImageWin
import os

""" ref: 
https://stackoverflow.com/questions/38178454/python27-on-windows-10-how-can-i-tell-printing-paper-size-is-50-8mm-x-25-4mm
"""
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

bPrintToPdf = 0
bPrintToPdf = 1
if bPrintToPdf: printer_name = "Microsoft Print to PDF"


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
    attributes['pDevMode'].PaperSize = 1


hDC = win32ui.CreateDC()

if 0:
    hDC.CreatePrinterDC( printer_name )
else:
    # configure printer
    hprinter = win32print.OpenPrinter(printer_name)
    devmode = win32print.GetPrinter(hprinter, 2)["pDevMode"]
    print("dir devmode: " + str(dir(devmode)))
    #interestingField = 'DisplayOrientation', 'Orientation', 'PanningHeight', 'PanningWidth', 'PaperLength', 'PaperSize', 'PaperWidth', 'PelsHeight'
    #Color=1 or 2 if color
    print("DisplayOrientation: " + str(devmode.DisplayOrientation))
    print("Orientation: " + str(devmode.Orientation))
    print("PaperSize: " + str(devmode.PaperSize))
    print("PaperWidth: " + str(devmode.PaperWidth))
    print("PaperLength: " + str(devmode.PaperLength))
    print("FormName: " + str(devmode.FormName))
    if 1:
        # force paper to be smaller (not sure it works)
        devmode.PaperWidth = 1040
        devmode.PaperLength = 760
    devmode.Orientation = 2 # 2 for landscape; 0 or 1 for portrait ?!?
    print("== modified")
    print("Orientation: " + str(devmode.Orientation))
    print("PaperWidth: " + str(devmode.PaperWidth))
    print("PaperLength: " + str(devmode.PaperLength))
    
    # explore forms, but don't know how to use it
    forms = win32print.EnumForms(hprinter) 
    strWantedForm = "stickers_ochateau"
    #~ print("forms: " + str(forms))
    for f in forms:
        strName = f["Name"]
        #~ print(strName)
        if strName == strWantedForm:
            selected_form = f
            break
    print("selected_form:" + str(selected_form)) # and so, what to do with that ?
    devmode.FormName = strWantedForm
    print("FormName: " + str(devmode.FormName))
        
            
    print("== apres forms")
    print("Orientation: " + str(devmode.Orientation))
    print("PaperWidth: " + str(devmode.PaperWidth))
    print("PaperLength: " + str(devmode.PaperLength))
    
    import win32gui
    handleDC = win32gui.CreateDC("WINSPOOL", printer_name, devmode)
    hDC = win32ui.CreateDCFromHandle(handleDC) # WRN: hDC is no more the handle but a python object representing the DC

printable_area = hDC.GetDeviceCaps (HORZRES), hDC.GetDeviceCaps (VERTRES)
printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)
printer_margins = hDC.GetDeviceCaps (PHYSICALOFFSETX), hDC.GetDeviceCaps (PHYSICALOFFSETY)

print("printer_size: %s" % str(printer_size))
print("printable_area: %s" % str(printable_area))
print("printer_margins: %s" % str(printer_margins))

if 0:
    # reduce papersize
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
    bmp = bmp.rotate(90, expand=True) # expand: change size of destination image (and so no more black band) 
  
print("bmp.size (2): %s" % str(bmp.size))
print("realBmpSize: %s" % str(realBmpSize))
assert(realBmpSize==bmp.size) # assert expand do its job


ratios = [1.0 * printable_area[0] / realBmpSize[0], 1.0 * printable_area[1] / realBmpSize[1]]
print("scale: %s" % (ratios))
scale = min(ratios)
#~ scale = 1

#
# Start the print job, and draw the bitmap to
#  the printer device at the scaled size.
#
#~ exit(0)

dstFile = None
if bPrintToPdf: dstFile = "c:/tmp/out.pdf"
hDC.StartDoc(file_name,dstFile)
hDC.StartPage()

dib = ImageWin.Dib(bmp)
scaled_width, scaled_height = [int (scale * i) for i in realBmpSize]
print("scaled_width: %s, scaled_height: %s" % (scaled_width,scaled_height))
x1 = int ((printer_size[0] - scaled_width) / 2) # center on screen
y1 = int ((printer_size[1] - scaled_height) / 2)
x2 = x1 + scaled_width
y2 = y1 + scaled_height
print("x1: %s, y1: %s, x2: %s, y2: %s" % (x1,y1,x2,y2))
dib.draw (hDC.GetHandleOutput(), (x1, y1, x2, y2))

if 1:
    import win32con
    import win32api
    #~ win32gui.SetTextColor(handleDC, win32api.RGB(255,0,0)) # RGB
    win32gui.SetTextColor(handleDC, 0xFF0000) # BGR
    sizeTextRect = hDC.DrawText("TESTOR", (10, 10, 200, 200), win32con.DT_CENTER|win32con.DT_CALCRECT)
    print("sizeTextRect: %s" % str(sizeTextRect)) # seems not working (or only height!)
    
    # left top corner, right bottom corner
    hDC.DrawText("TEST", (10, 10, 300, 100), win32con.DT_CENTER)
    
    strLongText = "A very big long and boring text" # note the A and very are stuck together on print
    hDC.DrawText(strLongText, (10, 100, 900, 200), win32con.DT_CENTER)
    hDC.DrawText(strLongText, (10, 200, 900, 300), win32con.DT_CENTER|win32con.DT_WORD_ELLIPSIS)
    win32gui.SetBkColor(handleDC, 0xAAAAAA)
    hDC.DrawText(strLongText, (10, 300, 1200, 400), win32con.DT_CENTER)
    hDC.DrawText(strLongText, (1000, 400, 2200, 500), win32con.DT_CENTER)
    win32gui.SetBkMode(handleDC, 0) # 0: transparent (and 1)
    hDC.DrawText(strLongText, (1000, 500, 2200, 600), win32con.DT_CENTER)
    win32gui.SetBkMode(handleDC, 2) # 2: opaque 
    hDC.DrawText(strLongText, (1000, 600, 2200, 700), win32con.DT_CENTER)  
    # change font, thus text size
    fontSize = 120
    lf = win32gui.LOGFONT()
    lf.lfFaceName = "Stencil"
    lf.lfHeight = fontSize
    lf.lfWeight = 100

    lf.lfQuality = win32con.NONANTIALIASED_QUALITY
    hf = win32gui.CreateFontIndirect(lf)
    win32gui.SelectObject(handleDC, hf)
    hDC.DrawText(strLongText, (1000, 700, 2800, 800), win32con.DT_CENTER)
    sizeTextRect = hDC.DrawText("TESTOR", (10, 10, 200, 200), win32con.DT_CENTER|win32con.DT_CALCRECT)
    print("sizeTextRect: %s" % str(sizeTextRect)) # seems not working  (or only height!)
    
    lf.lfWeight = 800
    hf = win32gui.CreateFontIndirect(lf)
    win32gui.SelectObject(handleDC, hf)
    hDC.DrawText(strLongText, (1000, 800, 2800, 900), win32con.DT_CENTER)

hDC.EndPage()
hDC.EndDoc()
hDC.DeleteDC()

if bPrintToPdf: os.system( "start " + dstFile )