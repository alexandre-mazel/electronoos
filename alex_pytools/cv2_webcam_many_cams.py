import numpy as np
import cv2
import time

import threading

import misctools

class VideoCaptureAsync:
    """
    found that on the web, author said it's faster, I think it doesn't wait for the image to be completed.
    At least it doesn't stuck the main thread...
    """
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()
        
# VideoCaptureAsync - end

aCap = []
for i in range(10):
    oneCap = cv2.VideoCapture(i) #or 0 + cv2.CAP_DSHOW
    oneCap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    oneCap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    if oneCap.isOpened():
        aCap.append(oneCap)

print("nbr cam: %d" % len(aCap))
if len(aCap) < 1:
    exit(0)

nCptFrame = 0
timeBegin = time.time()
bFirstTime = 1
while(True):
    for i in range(len(aCap)):        
        ret, frame = aCap[i].read()
        #~ print("ret: %s" % ret)
        if ret == False:
            print("WRN: can't get image from camera %d" % i )
            time.sleep(0.3)
            continue

        if bFirstTime:
            bFirstTime = 0
            print("image properties: %s" % str(frame.shape) )
        
        # Our operations on the frame come here
        #~ gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #~ frame = np.rot90(frame)
        #~ frame = cv2.resize(frame, None, fx=1.5, fy=1.5 )

        if 0:
            fn = misctools.getFilenameFromTime() + "_" + str(i) + ".jpg"
            fn = "d:/tmp/" + fn
            retVal = cv2.imwrite(fn, frame )
            assert(retVal)
            print("INF: output to '%s'" % fn )

        # Display the resulting frame
        cv2.imshow('frame_' + str(i),frame)
        #~ cv2.imshow('gray',gray)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
    nCptFrame += 1
    if nCptFrame > 60:
        t = time.time() - timeBegin
        print("fps: %5.2fs" % (nCptFrame / t) )
        nCptFrame = 0
        timeBegin = time.time()

    #~ time.sleep(0.01)
        
        
    # D415: 60fps up to 1280x720 RGB


        


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()