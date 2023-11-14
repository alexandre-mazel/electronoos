import win32print # pip install pywin32
import win32ui
from PIL import Image, ImageWin # pip install Pillow
import os

####################################
#
#   Script to send automatically a stickers to the printers
#   (c) 2023 A.Mazel
#
#   v1.0
# 
####################################

# construct from print_with_win32_print_alt and https://stackoverflow.com/questions/38178454/python27-on-windows-10-how-can-i-tell-printing-paper-size-is-50-8mm-x-25-4mm

def printImg(strFilename):
    """
    print an image in the Cave du Louvre printers (correct paper settings needs to be set by default)
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
    print("printer_name: " + printer_name)


    if 0:
        hDC.CreatePrinterDC( printer_name )
    else:
        # configure printer
        PRINTER_DEFAULTS = {"DesiredAccess":win32print.PRINTER_ALL_ACCESS}
        hprinter = win32print.OpenPrinter(printer_name,PRINTER_DEFAULTS)
        printer_attr = win32print.GetPrinter(hprinter, 2)
        devmode = printer_attr["pDevMode"]
        
        print("dir devmode: " + str(dir(devmode)))
        #interestingField = 'DisplayOrientation', 'Orientation', 'PanningHeight', 'PanningWidth', 'PaperLength', 'PaperSize', 'PaperWidth', 'PelsHeight'
        #Color=1 or 2 if color
        print("DisplayOrientation: " + str(devmode.DisplayOrientation))
        print("Orientation: " + str(devmode.Orientation))
        print("PaperSize: " + str(devmode.PaperSize))
        print("PaperWidth: " + str(devmode.PaperWidth))
        print("PaperLength: " + str(devmode.PaperLength))
        print("FormName: " + str(devmode.FormName))
        if 0:
            # force paper to be smaller (not sure it works)
            devmode.PaperWidth = 1040
            devmode.PaperLength = 760
        devmode.Orientation = 2 # 2 for landscape; 0 or 1 for portrait ?!?
        print("== modified")
        print("Orientation: " + str(devmode.Orientation))
        print("PaperWidth: " + str(devmode.PaperWidth))
        print("PaperLength: " + str(devmode.PaperLength))
        
        # explore forms and set them
        # I change that: I put this settings as default in the window printer settings
        if 0:
            forms = win32print.EnumForms(hprinter) 
            strWantedForm = "stickers_bouteille"
            strWantedForm = "stickers_ochateau" # bizarre, c'est pas ce nom la dans les form!
            #~ print("forms: " + str(forms))
            for f in forms:
                strName = f["Name"]
                if "tick" in strName: print("DBG: found form looks like: " + strName)
                if strName == strWantedForm:
                    selected_form = f
                    break
            else:
                print("WRN: form %s not found" % strWantedForm)
            print("selected_form:" + str(selected_form)) # and so, what to do with that ?
            devmode.FormName = strWantedForm
            print("FormName: " + str(devmode.FormName))
            
            # setting printer mode
            print("printer_attr: %s" % str(printer_attr))
            print("printer_attr.FormName: %s" % str(printer_attr["pDevMode"].FormName))
            print("printer_attr.PaperLength: %s" % str(printer_attr["pDevMode"].PaperLength))
            win32print.SetPrinter(hprinter, 2,printer_attr,0)
                
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

    #
    # Open the image, rotate it if it's wider than
    #  it is high, and work out how much to multiply
    #  each pixel by to get it as big as possible on
    #  the page without distorting.
    #

    bmp = Image.open( strFilename )

    print("bmp.size (1): %s" % str(bmp.size))
    realBmpSize = (bmp.size[0],bmp.size[1])


    print("bmp.size (2): %s" % str(bmp.size))
    print("realBmpSize: %s" % str(realBmpSize))
    assert(realBmpSize==bmp.size) # assert expand do its job


    ratios = [1.0 * printable_area[0] / realBmpSize[0], 1.0 * printable_area[1] / realBmpSize[1]]
    print("scale: %s" % (ratios))
    scale = min(ratios)
    scale *= 1.03 # zoom un peu car on sait que les etiquettes ont un peu de blanc autour
    #~ scale = 1

    #
    # Start the print job, and draw the bitmap to
    #  the printer device at the scaled size.
    #

    #~ exit(0)

    dstFile = None
    hDC.StartDoc(strFilename,dstFile)
    hDC.StartPage()

    dib = ImageWin.Dib(bmp)
    scaled_width, scaled_height = [int (scale * i) for i in realBmpSize]
    print("scaled_width: %s, scaled_height: %s" % (scaled_width,scaled_height))
    x1 = int ((printer_size[0] - scaled_width) / 2) # center on screen
    y1 = int ((printer_size[1] - scaled_height) / 2)
    x1 = printer_margins[0] # don't want to center on this printer
    x1 = 0
    y1 = 0 # pas sur de celui la
    x2 = x1 + scaled_width
    y2 = y1 + scaled_height
    print("x1: %s, y1: %s, x2: %s, y2: %s" % (x1,y1,x2,y2))
    dib.draw (hDC.GetHandleOutput(), (x1, y1, x2, y2))

    hDC.EndPage()
    hDC.EndDoc()
    hDC.DeleteDC()
    
    
# printImg - end


if __name__ == "__main__":        
    strFilename = "C:/Users/alexa/perso/docs/2023-10_cdl_photosbooths/stickers.jpg"
    printImg(strFilename)
