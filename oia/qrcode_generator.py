import qrcode # pip3 install qrcode
# example data
data = "http://engrenage.studio/oia/OIA_2022_2023_Cycle1.pdf"
#~ data = "http://engrenage.studio/vcards/alexandre.htm"
data = "http://obo-world.com"
data = "mailto:alexandre.zelma@gmail.com?subject=Location%20Studio%20Sceaux.&body=Monsieur,%20votre%20annonce%20m%20interesse%20enormement..."
data = "mailto:alexandre.zelma@gmail.com?subject=Location%20Studio%20Sceaux."
data = "tel:+33610601979"
data = "http://obo-world.com/presence.htm?c=kendo&l=123"
# output file name
filename = "oia_cycle_x.png"
# generate qr code
img = qrcode.make(data)
# save img to a file
img.save(filename)
print("SUCCESS: QRCode written to file " + filename )
print("size: %dx%d (pixel size:%s)"  % (img.width, img.height, img.pixel_size) )


# et si on l'affichait juste pour voir, ca serait plus poli
import cv2
img=cv2.imread(filename)
cv2.imshow("result: " + filename,img)
cv2.waitKey(0)