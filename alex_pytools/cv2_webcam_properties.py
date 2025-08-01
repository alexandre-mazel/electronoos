import cv2
import time


all_resolution_possible = [
    (160, 120),

	(192, 144),
	(256, 144),

	(240, 160),

	(320, 240),
	(360, 240),
	(384, 240),
	(400, 240),
	(432, 240),

	(480, 320),

	(480, 360),
	(640, 360),

	(600, 480),
	(640, 480),
	(720, 480),
	(768, 480),
	(800, 480),
	(854, 480),
	(960, 480),

	(675, 540),
	(960, 540),

	(720, 576),
	(768, 576),
	(1024, 576),

	(750, 600),
	(800, 600),
	(1024, 600),

	(960, 640),
	(1024, 640),
	(1136, 640),

	(960, 720),
	(1152, 720),
	(1280, 720),
	(1440, 720),

	(960, 768),
	(1024, 768),
	(1152, 768),
	(1280, 768),
	(1366, 768),

	(1280, 800),

	(1152, 864),
	(1280, 864),
	(1536, 864),

	(1200, 896),
	(1440, 896),
	(1600, 896),

	(1200, 900),
	(1440, 900),
	(1600, 900),

	(1280, 960),
	(1440, 960),
	(1536, 960),

	(1280, 1024),
	(1600, 1024),

	(1400, 1050),
	(1680, 1050),

	(1440, 1080),
	(1920, 1080),
	(2160, 1080),
	(2280, 1080),
	(2560, 1080),

	(2048, 1152),

	(1500, 1200),
	(1600, 1200),
	(1920, 1200),

	(1920, 1280),
	(2048, 1280),

	(1920, 1440),
	(2160, 1440),
	(2304, 1440),
	(2560, 1440),
	(2880, 1440),
	(2960, 1440),
	(3040, 1440),
	(3120, 1440),
	(3200, 1440),
	(3440, 1440),
	(5120, 1440),

	(2048, 1536),

	(2400, 1600),
	(2560, 1600),
	(3840, 1600),

	(2880, 1620),

	(2880, 1800),
	(3200, 1800),

	(2560, 1920),
	(2880, 1920),
	(3072, 1920),

	(2560, 2048),
	(2732, 2048),
	(3200, 2048),

	(2880, 2160),
	(3240, 2160),
	(3840, 2160),
	(4320, 2160),
	(5120, 2160),

	(3200, 2400),
	(3840, 2400),

	(3840, 2560),
	(4096, 2560),

	(5120, 2880),
	(5760, 2880),

	(4096, 3072),

	(7680, 4320),
	(10240, 4320),
]

def get_hostname():
    import socket
    return socket.gethostname()

def get_available_cameras() :
    """
    mstab7:
    {0: 'Surface Camera Front', 1: 'Surface Camera Rear', 2: 'EOS Webcam Utility', 3: 'HD Pro Webcam C920', 4: 'GoPro Webcam'}
    """
    
    import pygrabber.dshow_graph # pip install pygrabber

    devices = pygrabber.dshow_graph.FilterGraph().get_input_devices()

    available_cameras = {}

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name

    return available_cameras
    
def get_available_cameras_alt():
    """
    result example: opencv_index: 0, device_name: Integrated Webcam
    
    https://github.com/pvys/CV-camera-finder
    
    Dependency: Visual C++ Redistributable 2019

    You can download it here: https://support.microsoft.com/ko-kr/help/2977003/the-latest-supported-visual-c-downloads

    "Tested Env: windows10, python3." not tested by Alexandre
    """
    from pymf import get_MF_devices
    device_list = get_MF_devices()
    for i, device_name in enumerate(device_list):
        print(f"opencv_index: {i}, device_name: {device_name}")
    
def get_available_microphones() :
    """
    mstab7: 
    {0: 'Microsoft Sound Mapper - Input', 1: 'Microphone (HD Pro Webcam C920)', 2: 'Réseau de microphones (2- Realt', 
    3: 'Hi-Fi Cable Output (VB-Audio Hi', 4: 'CABLE Output (VB-Audio Virtual '}

    """
    import pyaudio  # pip install pyaudio
    available_microphones = {}
    pyduo = pyaudio.PyAudio()
    devices_info = pyduo.get_host_api_info_by_index(0)
    number_of_devices = devices_info.get('deviceCount')
    for device_index in range(0, number_of_devices):
        if (pyduo.get_device_info_by_host_api_device_index(0, device_index).get('maxInputChannels')) > 0:
            available_microphones[device_index] = pyduo.get_device_info_by_host_api_device_index(0, device_index).get('name')

    return available_microphones

def get_capacity():
    """
    mstab7:
    {0: 'Surface Camera Front', 1: 'Surface Camera Rear', 2: 'EOS Webcam Utility', 3: 'HD Pro Webcam C920', 4: 'GoPro Webcam'}
    
    avec id_base a 0 ca va super vite, mais les resultats ne sont pas tres reels (eg: juste du 30 fps) et ca gel sur la 3: HD Pro Webcam C920
    avec id_base a CAP_DSHOW, on a du 240 partout, mais chaque resolution est lente a teste et fait clignoter la camera...
    (par exemple aussi ca accepte la resolution 640x360 et la 1280x720 et la hd sur la Surface camera Rear alors que pas sur la base 0) 
    specif officielle:  Camera frontale 5.0MP avec video Full HD 1080p, Camera arriere 8 Mpx avec mise au point automatique et qualite video Full HD 1080p

    """
    
    bVerbose = 1
    bVerbose = 0
    
    bRenderOneImageEachResolution = 1
    bRenderOneImageEachResolution = 0
    
    hostname = get_hostname()
    
    cap_mode = cv2.CAP_ANY
    list_base = [0,cv2.CAP_DSHOW] # CAP_DSHOW has a value of 700
    list_base = [cv2.CAP_DSHOW]
    for id_base in list_base:
        
        id = 0
        
        #~ id = 3 # start from specific idx
        
        nbr_error = 0
        
        while 1:
            numcam = id_base + id
            
            if nbr_error > 2:
                break # no more camera
            
            last_err = ""
            
            if numcam == 3 and hostname == "MSTAB7":
                continue
            
            if bVerbose: print( "    (opening %d...)" % (numcam) )
            cam = cv2.VideoCapture( numcam, cap_mode )
            if not cam.isOpened():
                nbr_error += 1
                continue
            
            print( "camera id %d" % (numcam) )
            
            name = cam.getBackendName()
            print( "name: '%s'" % (name) ) # name: 'DSHOW' (pour la base a 700)
                        
            for res in all_resolution_possible:
                w,h = res
                
                # filter on just a forgotten height resolution
                if 0 and (h != 720 or h != 896):
                    continue
                            
                cam.set( cv2.CAP_PROP_FRAME_WIDTH, w )
                cam.set( cv2.CAP_PROP_FRAME_HEIGHT, h )
                cam.set( cv2.CAP_PROP_FPS, 240 )
                
                getw = cam.get( cv2.CAP_PROP_FRAME_WIDTH )
                geth = cam.get( cv2.CAP_PROP_FRAME_HEIGHT )
                getfps = cam.get( cv2.CAP_PROP_FPS )
                
                if getw == w and geth == h:
                    
                    bTestRealFps = True
                    
                    end = "\n" # default
                    if bTestRealFps:
                        end = ""
                        
                    print( "  resolution %dx%d @ %d fps" % (w,h,getfps), end=end )
                 
                    if bTestRealFps:
                        # test reel:
                        nbr_image = 0
                        time_begin = time.time()
                        for i in range( 100 ):
                            try:
                                success, frame = cam.read()
                                if success:
                                    if bRenderOneImageEachResolution:
                                        if nbr_image == 3: # les 2 premieres peuvent etre noires
                                            cv2.imshow( "cam %d %dx%d" % (numcam, getw, geth ), frame )
                                    nbr_image += 1
                            except cv2.error as err:
                                if str(err) != last_err:
                                    last_err = str(err)
                                    print( "WRN: get_capacity: cv2.error: %s" % last_err )
                                # cv2.error: Unknown C++ exception from OpenCV code
                                
                            time.sleep(0.001) # sinon ca crashe dans certains python
                            
                            if time.time() - time_begin > 5:
                                break
                        duration = time.time() - time_begin
                        measured_fps = nbr_image / duration
                        print( "    measured_fps: %.1f fps" % measured_fps )
                        if bRenderOneImageEachResolution: cv2.waitKey( 500 )
                else:
                    if bVerbose: print( "    (tested %dx%d)" % (w,h) )
                    if bRenderOneImageEachResolution: cv2.waitKey( 100 )

            # for each res - end
            
            cam.release()
            id += 1
            
        # while - end
        
        if bRenderOneImageEachResolution:
            cv2.waitKey( 0 )

# get_capacity - end

"""
hostname: MSTAB7
{0: 'Surface Camera Front', 1: 'Surface Camera Rear', 2: 'EOS Webcam Utility', 3: 'HD Pro Webcam C920', 4: 'GoPro Webcam'}
{0: 'Microsoft Sound Mapper - Input', 1: 'Microphone (HD Pro Webcam C920)', 2: 'Réseau de microphones (2- Realt', 3: 'Hi-Fi Cable Output (VB-Audio Hi', 4: 'CABLE Output (VB-Audio Virtual '}
camera id 700
name: 'DSHOW'
  resolution 640x360 @ 240 fps
    measured_fps: 29.3 fps
  resolution 640x480 @ 240 fps
    measured_fps: 29.3 fps
  resolution 1280x720 @ 240 fps
    measured_fps: 29.1 fps
  resolution 1920x1080 @ 240 fps
    measured_fps: 28.3 fps
  resolution 1920x1280 @ 240 fps
    measured_fps: 28.7 fps
  resolution 1920x1440 @ 240 fps
    measured_fps: 28.6 fps
camera id 701
name: 'DSHOW'
  resolution 640x360 @ 240 fps
    measured_fps: 29.1 fps
  resolution 640x480 @ 240 fps
    measured_fps: 29.4 fps
  resolution 1280x720 @ 240 fps
    measured_fps: 29.0 fps
  resolution 1920x1080 @ 240 fps
    measured_fps: 28.4 fps
  resolution 1920x1280 @ 240 fps
    measured_fps: 28.9 fps
  resolution 1920x1440 @ 240 fps
    measured_fps: 28.9 fps
camera id 702
name: 'DSHOW'
  resolution 1024x576 @ 240 fps
    measured_fps: 109.2 fps
camera id 703
name: 'DSHOW'
  resolution 160x120 @ 240 fps
    measured_fps: 19.8 fps
  resolution 320x240 @ 240 fps
    measured_fps: 14.4 fps
  resolution 432x240 @ 240 fps
    measured_fps: 14.4 fps
  resolution 640x360 @ 240 fps
    measured_fps: 14.6 fps
  resolution 640x480 @ 240 fps
    measured_fps: 14.6 fps
  resolution 1024x576 @ 240 fps
    measured_fps: 14.3 fps
  resolution 800x600 @ 240 fps
    measured_fps: 14.3 fps
  resolution 960x720 @ 240 fps
    measured_fps: 14.2 fps
  resolution 1280x720 @ 240 fps
    measured_fps: 9.4 fps
  resolution 1600x896 @ 240 fps    
    measured_fps: 7.0 fps <<<<<<<<<<<<
  resolution 1920x1080 @ 240 fps
    measured_fps: 4.6 fps

"""

if __name__ == "__main__":
    print("hostname: %s" % get_hostname() )
    print(get_available_cameras())
    #~ get_available_cameras_alt()
    print(get_available_microphones())
    get_capacity()
        
    