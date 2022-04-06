import cv2
import numpy as np
import time

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if (cap.isOpened() == False): 
  print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
#~ out = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc('x','2','6','4'), 20, (frame_width,frame_height))
out = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc('a','v','c','1'), frame_fps, (frame_width,frame_height))

timeBegin = time.time()
while(True):
  ret, frame = cap.read()

  if ret == True: 
    
    # Write the frame into the file 'output.avi'
    out.write(frame)

    if 0:
        # Display the resulting frame    
        cv2.imshow('frame',frame)

        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break
    else:
        if time.time()-timeBegin>2:
            break
        

  # Break the loop
  else:
    break  

# When everything done, release the video capture and video write objects
cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()
