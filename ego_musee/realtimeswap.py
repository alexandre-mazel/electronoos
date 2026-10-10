import cv2
import random
import time

import generate_faceswap

def realtime_swap( listPaintings ):
    
    camera = cv2.VideoCapture ( 0 )

    if not camera.isOpened ( ):
        print( "ERR: realtime_swap: can't open camera" )
        return 
        
    generate_faceswap.create_generator()
        
    bufpainting = None
    painting_filename_prev = ""
    facepainting = []
    while 1:
        # pick an image
        idx = random.randint( 0, len(listPaintings)-1 )
        painting_filename = listPaintings[idx]
        if painting_filename != painting_filename_prev:
            absf = "paintings/" + painting_filename
            bufpainting = cv2.imread( absf )
            painting_faces = generate_faceswap.app.get(bufpainting)
            painting_face = painting_faces[0]
            result = bufpainting
        
        # l'image en reelle
        if not generate_faceswap.fade_images_buf( bufpainting, bufpainting, "Mona Lisa by Leonardo da Vinci", 1, True ):
            break
            
        while True:
            result_prev = result
            success, frame = camera.read()
            if success:
                print( "Detection visage" )
                time_begin = time.time()
                camera_faces = generate_faceswap.app.get(frame)
                duration = time.time() - time_begin ; time_begin = time.time()
                print( "duration extract face camera: %.3fs" % duration )
                if len( camera_faces ) > 0:
                        camera_face = camera_faces[0]
                        result = generate_faceswap.swapper.get( bufpainting, painting_face, camera_face,  paste_back = True )
                        duration = time.time() - time_begin ; time_begin = time.time()
                        print( "duration swap: %.3fs" % duration )
                        print( "drawing swapped..." )
                        if not generate_faceswap.fade_images_buf( result_prev, result, "Mona Lisa by Leonardo da Vinci", 5, True ):
                            break
                else:
                        print( "drawing original back..." )
                        result = bufpainting
                        if not generate_faceswap.fade_images_buf( result_prev, result, "Mona Lisa by Leonardo da Vinci", 2, True ):
                            break
        


if __name__ == "__main__":
    listPaintings = ["Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched_avg.jpg"]
    realtime_swap(listPaintings)

