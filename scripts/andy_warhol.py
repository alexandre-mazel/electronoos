import cv2
import numpy as np
strPath = "C:/Users/amazel/perso/docs/Option_IA/"
im = cv2.imread(strPath + "nao_eod.png")
im = cv2.imread(strPath + "flowers.jpg")
im = cv2.imread(strPath + "sunflowers.jpg")
im = cv2.imread(strPath + "monroe.jpg")
h,w = im.shape[:2]
painting = np.zeros((h*2,w*3,3),dtype=np.uint8)

im1 = im.copy()
im2 = im.copy()
im3 = im.copy()
im4 = im.copy()
im5 = im.copy()
im6 = im.copy()

im1[:,:,0] = 0

im2[:,:,0] = im1[:,:,1]
im2[:,:,1] = im1[:,:,2]

im3[:,:,1] = 0
im4[:,:,2] = 0
im5[:,:,2] = 255

im6[:,:,1] = im6[:,:,0]
im6[:,:,0] = 255

painting[0:h,0:w] = im1
painting[0:h,w:w*2] = im2
painting[0:h,w*2:] = im3
painting[h:,0:w] = im4
painting[h:,w:w*2] = im5
painting[h:,w*2:] = im6

cv2.imshow("andy", painting )
cv2.waitKey(0)

cv2.imwrite("/tmp10/andy.png", painting)


