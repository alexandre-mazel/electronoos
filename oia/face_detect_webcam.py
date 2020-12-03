import cv2

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


cap = cv2.VideoCapture(0) #ouvre la webcam


while 1:
    
    ret, img = cap.read() # lis et stocke l'image dans frame
    
    #~ img = cv2.resize(img, None, fx=2,fy=2)

    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if 0:
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
    if 1:
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
        
    # Display the output
    cv2.imshow('img', img)
    key = cv2.waitKey(1)
    
    if key == 27:
        break