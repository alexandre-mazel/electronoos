import cv2
import numpy as np

def create():
	w=1920
	h=1080
	im = np.zeros((h,w,3), np.uint8)
	im[:] = (255,255,255)
	return im
	

def render(  im, objects, nIdxSelected = None ):	
	aPos = ((200,400), (860,700),(1300,400) )
	
	nPos = 0
	for o in objects:
		color = (255,0,0) 
		if nIdxSelected != None and nPos == nIdxSelected:
			color = ( 255, 0, 255 )
		cv2.putText( im, o, aPos[nPos], cv2.FONT_HERSHEY_SIMPLEX, 4, color, 6)
		nPos += 1
		
def draw( im, nTime ):
	strWindowName = "im"
	cv2.namedWindow( strWindowName, cv2.WINDOW_AUTOSIZE )
	cv2.moveWindow( strWindowName, 0, -40 )	
	cv2.imshow( strWindowName, im )
	nKey = cv2.waitKey(nTime)	
	if nKey == 27:
		exit(1)
	
im = create()
while( 1 ):
	render( im, ("Car", "Dog", "Cat"), None )
	draw(im, 2000)
	render( im, ("Car", "Dog", "Cat"), 0 )
	draw(im, 2000)
	render( im, ("Car", "Dog", "Cat"), 1 )
	draw(im, 2000)
	render( im, ("Car", "Dog", "Cat"), 2 )
	draw(im, 2000)