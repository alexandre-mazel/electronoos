import cv2

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Read the input image
img = cv2.imread('../data/inconnus.jpg')
img = cv2.imread("../data/fruit_face.jpg")

# Convert into grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detect faces
faces = face_cascade.detectMultiScale(gray, 1.1, 4)

# Draw rectangle around the faces
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    img[y:y+h//2,x:x+w//2,0]=0
    img[y:y+h//2,x:x+w//2,1]=0
    
# Display the output
cv2.imshow('img', img)
cv2.waitKey()