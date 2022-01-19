# -*- coding: cp1252 -*-

# sympathic stuffs for cv2

import cv2

def drawHighligthedText(im,txt, position, fontface=cv2.FONT_HERSHEY_SIMPLEX, fontscale = 1,color = (255,255,255), thickness = 1, color_back=(127,127,127)):
    """
    render a text with a painted bounding box (highlighted)
    """
    
    textsize, baseline = cv2.getTextSize(txt, fontFace, fontscale, fontthickness)
    cv2.rectangle( im, position, (position[0]+textsize[0],position[0]+textsize[1]),color_back)
    cv2.puttext(im,txt, position, fontface, fontscale,color,thickness)
        