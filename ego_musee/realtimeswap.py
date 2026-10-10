import cv2
import random
import time

import generate_faceswap

def is_screen_orientation_portrait():
    import ctypes
    user32 = ctypes.windll.user32
    orientation = user32.GetDisplayConfigBufferSizes

    from ctypes import wintypes

    class DisplayDevice ( ctypes.Structure ):
        _fields_ = [
            ( "cb", wintypes.DWORD ),
            ( "DeviceName", wintypes.WCHAR * 32 ),
            ( "StateFlags", wintypes.DWORD ),
            ( "DeviceID", wintypes.WCHAR * 128 ),
            ( "DeviceKey", wintypes.WCHAR * 128 )
        ]

    device = DisplayDevice ( )
    device.cb = ctypes.sizeof ( DisplayDevice )

    if user32.EnumDisplayDevicesW ( None, 0, ctypes.byref ( device ), 0 ):
        mode = ctypes.create_string_buffer ( 220 )
        result = user32.EnumDisplaySettingsW (
            device.DeviceName,
            -1,
            mode
        )

        if result:
            width = int.from_bytes ( mode[ 172:176 ], "little" )
            height = int.from_bytes ( mode[ 176:180 ], "little" )

            if height > width:
                return 1
            return 0

    return -1

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
                if is_screen_orientation_portrait():
                    frame = cv2.rotate ( frame, cv2.ROTATE_90_CLOCKWISE )
                    
                if 1:
                    # render image from camera
                    cv2.imshow( "camera", frame )
                    cv2.moveWindow ( "camera", 0, 600 )
                    cv2.waitKey(100)
                    
                print( "Detection visage" )
                time_begin = time.time()
                camera_faces = generate_faceswap.app.get(frame)
                duration = time.time() - time_begin ; time_begin = time.time()
                print( "duration extract face camera: %.3fs" % duration )
                if len( camera_faces ) > 0:
                    camera_face = camera_faces[0]
                    if 0:
                        # render face
                        #~ bbox = camera_face.bbox # copier la bbox du visage
                        cv2.imshow( "face", frame )
                        cv2.waitKey(100)
                    result = generate_faceswap.swapper.get( bufpainting, painting_face, camera_face,  paste_back = True )
                    duration = time.time() - time_begin ; time_begin = time.time()
                    print( "duration swap: %.3fs" % duration )
                    print( "drawing swapped..." )
                    output = "output/%08d.jpg" % int(time.time())
                    cv2.imwrite( output, result)
                    if not generate_faceswap.fade_images_buf( result_prev, result, "Mona Lisa by Leonardo da Vinci", 5, True ):
                        break
                else:
                    print( "drawing original back..." )
                    result = bufpainting
                    if not generate_faceswap.fade_images_buf( result_prev, result, "Mona Lisa by Leonardo da Vinci", 2, True ):
                        break
    


if __name__ == "__main__":
    listPaintings = ["Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched_avg.jpg"] # Entre 3.6 et 6.2 on my tab7
    listPaintings = ["Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched_small.jpg"] # 2.7 - 3.7
    realtime_swap(listPaintings)

