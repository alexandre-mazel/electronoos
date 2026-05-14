import win32print
import win32ui
from PIL import Image, ImageWin

PHYSICALWIDTH = 110
PHYSICALHEIGHT = 111

printer_name = win32print.GetDefaultPrinter ()
print("printer_name: " + printer_name)

file_name = "new.jpg"

hDC = win32ui.CreateDC()
hDC.CreatePrinterDC( printer_name )
printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)

print("printer_size: " + str(printer_size))

#~ file_name = "c:/users/alexa/downloads/stickers.jpg"
file_name = "C:/Users/alexa/perso/docs/2023-10_cdl_photosbooths/stickers.jpg"

bmp = Image.open (file_name)
if bmp.size[0] < bmp.size[1]:
  bmp = bmp.rotate(90)

hDC.StartDoc (file_name)
hDC.StartPage()

if 0:
    # fonctionne ok, mais n'enleve pas les bandes noires
    img_background = Image.new('RGB', (300, 200), (127, 127, 127))
    dib_background = ImageWin.Dib( img_background )
    #~ dib_background.expose( hDC.GetHandleOutput())
    dib_background.draw( hDC.GetHandleOutput(),(0,0,printer_size[0],printer_size[1]//2))


dib = ImageWin.Dib( bmp )

rCoef = 0.9
nMargin = 100
# first number is the width of the printer (the height of the stickers)
# quand on regarde le rouleur qui sort, les 2 premiers chiffres semblent ne rien changer!
dib.draw( hDC.GetHandleOutput(), (nMargin,nMargin,int(printer_size[0]*rCoef)-nMargin,int((printer_size[1]*0.7)*rCoef)-nMargin ) )

hDC.EndPage()
hDC.EndDoc()
hDC.DeleteDC()