# -*- coding: cp1252 -*-

# sympathic stuffs for cv2

import cv2
print("INF: cv2_tools: using CV2 version: %s" % cv2. __version__ )
import numpy as np

def drawHighligthedText(im,txt, position, fontface=cv2.FONT_HERSHEY_SIMPLEX, fontscale = 1,color = (255,255,255), thickness = 1, color_back=(127,127,127)):
    """
    render a text with a painted bounding box (highlighted)
    """
    
    textsize, baseline = cv2.getTextSize(txt, fontface, fontscale, thickness)
    print("textsize: %s, baseline: %s" % (textsize, baseline) )
    # on ajoute des +1 et +2 pour aerer
    nExtraLeft = thickness//2+1
    nExtraBottom = thickness//2+2
    if "q" in txt or 'g' in txt or 'p' in txt:
        nExtraBottom = int(baseline*4/5)+2+1
    cv2.rectangle( im, (position[0]-nExtraLeft,position[1]+nExtraBottom), (position[0]+textsize[0],position[1]-textsize[1]-1-2),color_back,-1)
    cv2.putText(im,txt, position, fontface, fontscale,color,thickness)
    
    
def autoTest():
    im = np.zeros((600,800,3),dtype=np.uint8)
    drawHighligthedText( im, "drawHighligthedText", (50,50))
    drawHighligthedText( im, "aa", (50,100))
    drawHighligthedText( im, "MM", (50,150))
    drawHighligthedText( im, "MM", (50,400),fontscale=4, thickness=12)
    drawHighligthedText( im, "tglq", (300,400),fontscale=4, thickness=12)
    drawHighligthedText( im, "tglq", (300,100),fontscale=1, thickness=20)
    drawHighligthedText( im, "tglq", (300,250),fontscale=4, thickness=1)
    drawHighligthedText( im, "M", (400,100),fontscale=4, thickness=1)
    drawHighligthedText( im, "Le petit chaperon rouge!", (20,500),fontscale=1, thickness=1)
    drawHighligthedText( im, "Toto est cool.", (400,550),fontscale=1, thickness=1)
    cv2.imshow("cv2_tools",im)
    key=cv2.waitKey(1) # time for image to refresh even if continuously pressing a key
    key=cv2.waitKey(0)


if __name__ == "__main__":
    pass
    autoTest()