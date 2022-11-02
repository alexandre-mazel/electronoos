import math

def getValue( t ):
    y = math.cos(t)
    return y
    
def renderIntestin( img, listVal ):
    """
    dessine le decor sous forme de rectangle empilée
    """
    ...
    
    #~ cv2.rectangle(image, start_point, end_point, color, thickness)
    
    cv2.rectangle(img, pt1, pt2, color)
    
    XXXXXXXXXXXX
    XXXXXXX
    XXXXXXXXXXXX
    XXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXX
    XXXXXXX
    




def renderGame():
    if 1:
        listValue = [100,200,100,300,400,500] 
    else:
        listValue = []
        for x in range(10):
            val = getValue(x/10.)
            print(val)
            listValue.append(val*400)
            
            
    w = 800
    h = 600
    im = np.zeros((h,w,3), dtype=np.uint8)
    renderIntestin( im, listValue )
    cv2.waitKey(0)

if __name__ == '__main__':
    renderGame()
