import qrcode # pip3 install qrcode

def generateQR( filename,mailcode ):
    print("ING: generateQR: Generating to file: '%s'" % mailcode)
    print("ING: generateQR: Code: '%s'" % mailcode)
    
    img = qrcode.make(mailcode)
    
    img.save(filename)
    print("SUCCESS: QRCode written to file " + filename )
    print("size: %dx%d (pixel size:%s)"  % (img.width, img.height, img.pixel_size) )
    print("")
    

datas = {
                "sticker_qrcode_en_NUM": "mailto:photobooth.cdl%2BNUM@gmail.com?subject=My picture at the Caves du Louvre&body=Please%20attach%20your%20photo%20to%20this%20email.%0D%0A%0D%0ATips%3A%20Select%20%22large%20image%22%20size%20but%20not%20%22real%20size%22.",
                "sticker_qrcode_fr_NUM": "mailto:photobooth.cdl%2BNUM@gmail.com?subject=Ma photo aux Caves du Louvre&body=Attachez votre photo a cet email.\n\nConseil: selectionner une image de grande taille mais pas taille r%e9elle."
             }
             
for k,v in datas.items():
    for i in range(1,5):
        strFilename = k.replace("NUM",str(i))
        strMailCode = v.replace("NUM",str(i))
        generateQR(strFilename+".png",strMailCode)
    
