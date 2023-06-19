import cv2
import math
import numpy as np

def applyBumpSlow(img,x,y):
    radius = 30
    power = 1.6 # >1.0 for expansion, <1.0 for shrinkage
        
    height, width, _ = img.shape
    map_x = np.zeros((height,width),dtype=np.float32)
    map_y = np.zeros((height,width),dtype=np.float32)

    # create index map
    for i in range(height):
        for j in range(width):
            map_x[i][j]=j
            map_y[i][j]=i
            
    # deform around the right eye
    for i in range (-radius, radius):
        for j in range(-radius, radius):
            if (i**2 + j**2 > radius ** 2):
                continue

            if i > 0:
                map_y[y + i][x + j] = y + (i/radius)**power * radius
            if i < 0:
                map_y[y + i][x + j] = y - (-i/radius)**power * radius
            if j > 0:
                map_x[y + i][x + j] = x + (j/radius)**power * radius
            if j < 0:
                map_x[y + i][x + j] = x - (-j/radius)**power * radius
    warped = cv2.remap(img,map_x,map_y,cv2.INTER_LINEAR)
    return warped


class Bumper:
    def __init__( self, radius = 30, power = 1.6 ):
        self._generateBump(radius, power)
    
    def _generateBump(self, radius, power ):
        """
        power = 1.6 # >1.0 for expansion, <1.0 for shrinkage
        """
        """
        right_eye = 240,320

        height, width, _ = 480,640,2
        self.map_x = np.zeros((height,width),dtype=np.float32)
        self.map_y = np.zeros((height,width),dtype=np.float32)

        # create index map
        for i in range(height):
            for j in range(width):
                self.map_x[i][j]=j
                self.map_y[i][j]=i
                
        # deform around the right eye
        for i in range (-radius, radius):
            for j in range(-radius, radius):
                if (i**2 + j**2 > radius ** 2):
                    continue

                if i > 0:
                    self.map_y[right_eye[1] + i][right_eye[0] + j] = right_eye[1] + (i/radius)**power * radius
                if i < 0:
                    self.map_y[right_eye[1] + i][right_eye[0] + j] = right_eye[1] - (-i/radius)**power * radius
                if j > 0:
                    self.map_x[right_eye[1] + i][right_eye[0] + j] = right_eye[0] + (j/radius)**power * radius
                if j < 0:
                    self.map_x[right_eye[1] + i][right_eye[0] + j] = right_eye[0] - (-j/radius)**power * radius

        """
        # generate juste one displacement map and use it later
        # for each point, return an offset
        self.radius = radius
        self.map_x = np.zeros((radius*2,radius*2),dtype=np.int32)
        self.map_y = np.zeros((radius*2,radius*2),dtype=np.int32)
        for i in range (-radius, radius):
            for j in range(-radius, radius):
                if (i**2 + j**2 >= radius ** 2) or i == 0 or j == 0:
                    # out of sphere
                    pass
                    #~ self.map_x[j+radius,i+radius] = 9 # already set
                    #~ self.map_y[j,i] = 0 
                else:
                    self.map_x[j+radius,i+radius] = int(radius*2/i)
                    #~ self.map_y[j+radius,i+radius] = int(power*10*math.sin((math.pi/2)*i/radius))
                    self.map_y[j+radius,i+radius] = int(radius*2/j)
        print(self.map_x)
        print(self.map_y)
        
    def applyBump( self, img, x, y ):
        """
        warped = cv2.remap(img,self.map_x,self.map_y,cv2.INTER_LINEAR)
        return warped
        """
        warped = img.copy()
        for i in range (-self.radius, self.radius):
            for j in range(-self.radius, self.radius):
                xoff = self.map_x[j,i]
                yoff = self.map_y[j,i]
                warped[y+j+yoff,x+i+xoff] = img[y+j,x+i]
                
        return warped

# class Bumper - end

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(3) #ouvre la webcam # 3: camera en usb

bumper = Bumper(radius=9)

while 1:
    
    ret, img = cap.read() # lis et stocke l'image dans frame
    
    #~ img = cv2.resize(img, None, fx=2,fy=2)
    
    #~ img = cv2.flip(img,0) # flip vertic

    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 10)

    if 1:
        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
    if 0:
        # Blur faces
        for (x, y, w, h) in faces:
            # blur
            w -= 16
            h += 16
            blurred=img[y:y+h,x:x+w]
            blurred = cv2.GaussianBlur(blurred,(0,0),8)
            img[y:y+h,x:x+w]=blurred
    if 0:
        # swap faces (amusant mais ca fait pas naturel)
        if len(faces) > 1:
            x1, y1, w1, h1 = faces[0]
            f1 = img[y1:y1+h1,x1:x1+w1]
            
            x2, y2, w2, h2 = faces[1]
            f2 = img[y2:y2+h2,x2:x2+w2]     
            
            f1r = cv2.resize(f1, (w2,h2))
            f2r = cv2.resize(f2, (w1,h1))
            
            img[y1:y1+h1,x1:x1+w1] = f2r
            img[y2:y2+h2,x2:x2+w2] = f1r
            
    if 0:
        if len(faces) > 0:
            # bump
            #~ img = bumper.applyBump(img,100,100)
            for (x, y, w, h) in faces:
                img = applyBumpSlow( img, x+int(w/3), y+int(h/2.6) )
                img = applyBumpSlow( img, x+int(w*2/3), y+int(h/2.6) )
        
    # Display the output
    cv2.imshow('img', img)
    key = cv2.waitKey(1)
    
    if key == 27:
        break