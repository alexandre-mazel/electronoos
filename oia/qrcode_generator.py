import qrcode # pip3 install qrcode
# example data
data = "http://engrenage.studio/oia/OIA_2021_2022_Cycle2.pdf"
# output file name
filename = "oia_cycle_x.png"
# generate qr code
img = qrcode.make(data)
# save img to a file
img.save(filename)
print("SUCCESS: QRCode written to file " + filename )

# et si on l'affichait juste pour voir, ca serait plus poli
import cv2
img=cv2.imread(filename)
cv2.imshow("result: " + filename,img)
cv2.waitKey(0)