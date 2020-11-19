# Author: Gael Varoquaux <gael dot varoquaux at normalesup dot org>
# License: BSD 3 clause
# mods to use webcam: A.Mazel
# source controlled under electronoos.scripts

import time

# Standard scientific Python imports
import matplotlib.pyplot as plt

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split
import numpy as np

import cv2 # OpenCV: Open Computer Vision
    
# The digits dataset
digits = datasets.load_digits()
if 0:
    # affiche des images au hasard

    print("nbr images dans la base: %d" % len(digits.images))
    print(digits.images[0].shape)

    cv2.imshow("une image",cv2.resize(digits.images[0],(640,640)) )
    cv2.imshow("une autre image",cv2.resize(digits.images[100],(640,640)) )
    print("la premiere image: " + str(digits.target[0]))
    print("l'autre image: " + str(digits.target[100]))
    cv2.waitKey(0)
    exit(1)

# The data that we are interested in is made of 8x8 images of digits, let's
# have a look at the first 4 images, stored in the `images` attribute of the
# dataset.  If we were working from image files, we could load them using
# matplotlib.pyplot.imread.  Note that each image must have the same size. For these
# images, we know which digit they represent: it is given in the 'target' of
# the dataset.
_, axes = plt.subplots(2, 4)
images_and_labels = list(zip(digits.images, digits.target))
for ax, (image, label) in zip(axes[0, :], images_and_labels[:4]):
    ax.set_axis_off()
    ax.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    ax.set_title('Training: %i' % label)

# To apply a classifier on this data, we need to flatten the image, to
# turn the data in a (samples, feature) matrix:
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))

# Create a classifier: a support vector classifier
classifier = svm.SVC(gamma=0.001)

# Split data into train and test subsets
X_train, X_test, y_train, y_test = train_test_split(
    data, digits.target, test_size=0.5, shuffle=False)

timeBegin = time.time()
# We learn the digits on the first half of the digits
classifier.fit(X_train, y_train)
print("time: %.3f s" % (time.time()-timeBegin) )

# Now predict the value of the digit on the second half:
predicted = classifier.predict(X_test)

if 0:
    images_and_predictions = list(zip(digits.images[n_samples // 2:], predicted))
    for ax, (image, prediction) in zip(axes[1, :], images_and_predictions[:4]):
        ax.set_axis_off()
        ax.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
        ax.set_title('Prediction: %i' % prediction)
    print(digits.target[n_samples // 2:][:4])

    print("Classification report for classifier %s:\n%s\n"
          % (classifier, metrics.classification_report(y_test, predicted)))
    disp = metrics.plot_confusion_matrix(classifier, X_test, y_test)
    disp.figure_.suptitle("Confusion Matrix")
    print("Confusion matrix:\n%s" % disp.confusion_matrix)

    plt.show()
    
if 0:
    # get image from camera
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    
    while 1:
        ret, frame = cap.read()
        
        cv2.imshow("webcam", frame)
        if ( cv2.waitKey(1) & 255 ) == ord('q'):
            break
            
    cv2.imwrite("/tmp10/sample.png", frame )
    
if 1:
    frame = cv2.imread("../datas/sample4c.png")
    cv2.imshow("sample", frame)
    
    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    frame_grey = ~ frame_grey
    print(frame_grey.shape)
    
    frame_grey = frame_grey[60:-60,:] #remove black border
    cv2.imshow("sample_grey", frame_grey)
    
    frame_grey = frame_grey[40:-10,40:-70]
    
    low_lim = 100
    low_lim = 0
    #~ ret,frame_grey = cv2.threshold(frame_grey,low_lim,255,cv2.THRESH_TOZERO)
    ret,frame_grey = cv2.threshold(frame_grey,127,255,cv2.THRESH_BINARY)
    
    frame_grey_h = frame_grey.copy()
    #~ frame_grey_h = cv2.equalizeHist(frame_grey)
  
    cv2.imshow("sample_grey_reduced_histo", frame_grey_h )
  
    sgr = cv2.resize(frame_grey_h,(8,8)) 
    #~ sgr = digits.images[100]
    
    print( sgr.dtype )
    
    # convert sgr to match same style of data than digits
    sgr = sgr.astype(dtype=np.float64)
    
    sgr /= 16.
    print( "sgr:" + str(sgr.dtype) )
    print( sgr )
    print( "digits...:" + str(digits.images[100].dtype) )
    print( digits.images[100] )

    cv2.imshow("sample_grey_reduced", cv2.resize(sgr,(320,320),interpolation=cv2.INTER_NEAREST ) )
    cv2.imshow("sample as ref", cv2.resize(digits.images[100],(320,320),interpolation=cv2.INTER_NEAREST ) )
    
    cv2.waitKey(0)

    
    #~ predicted = classifier.predict(sgr.ravel()) #.ravel().reshape(1, -1)
    predicted = classifier.predict(sgr.ravel().reshape(1, -1))
    print("predicted: %s" % str(predicted) )
    # see confidence
    decision = classifier.decision_function(sgr.ravel().reshape(1, -1))
    decision = np.around(decision,decimals=2)
    decision = list(zip(range(10),decision[0]))
    print("decision: %s" % str(sorted(decision,key=lambda d: d[1], reverse=True) ) )
    