import cv2 as cv
import cv2

# ref:
# https://docs.opencv.org/4.x/d2/d94/bioinspired_retina.html
# and:
# https://docs.opencv.org/3.4/d3/d86/tutorial_bioinspired_retina_model.html
# api:
# https://docs.opencv.org/4.x/dc/d54/classcv_1_1bioinspired_1_1Retina.html


def acquire_camera():
    #setup webcam reader
    videoHandler = cv.VideoCapture(0)
    succeed, inputImage=videoHandler.read()
    #allocate a retina instance with input size equal to the one of the loaded image
    retina = cv.bioinspired_Retina.create((inputImage.shape[1], inputImage.shape[0]))

    #retina parameters management methods use sample

    #-> save current (here default) retina parameters to a xml file (you may use it only one time to get the file and modify it)
    #~ retina.write('retinaParams.xml')

    #-> load retina parameters from a xml file : here we load the default parameters that we just wrote to file
    retina.setup('retinaParams.xml')

    #main processing loop
    stillProcess=True
    while stillProcess is True:
        #grab a new frame and display it
        stillProcess, inputImage=videoHandler.read()
        cv.imshow('input frame', inputImage)
        
        #run retina on the input image
        retina.run(inputImage)
        
        #grab retina outputs
        retinaOut_parvo=retina.getParvo()
        retinaOut_magno=retina.getMagno()
        #draw retina outputs
        cv.imshow('retina parvo out', retinaOut_parvo)
        cv.imshow('retina magno out', retinaOut_magno)
        #wait a little to let the time for figures to be drawn
        cv.waitKey(2)
        
"""
Photo-receptors parameters

The following parameters act on the entry point of the retina - photo-receptors - and has impact on all of the following processes. These sensors are low pass spatio-temporal filters that smooth temporal and spatial data and also adjust their sensitivity to local luminance,thus, leads to improving details extraction and high frequency noise canceling.

    photoreceptorsLocalAdaptationSensitivity between 0 and 1. Values close to 1 allow high luminance log compression's effect at the photo-receptors level. Values closer to 0 provide a more linear sensitivity. Increased alone, it can burn the Parvo (details channel) output image. If adjusted in collaboration with ganglionCellsSensitivity,images can be very contrasted whatever the local luminance there is... at the cost of a naturalness decrease.
    photoreceptorsTemporalConstant this setups the temporal constant of the low pass filter effect at the entry of the retina. High value leads to strong temporal smoothing effect : moving objects are blurred and can disappear while static object are favored. But when starting the retina processing, stable state is reached later.
    photoreceptorsSpatialConstant specifies the spatial constant related to photo-receptors' low pass filter's effect. Those parameters specify the minimum value of the spatial signal period allowed in what follows. Typically, this filter should cut high frequency noise. On the other hand, a 0 value cuts none of the noise while higher values start to cut high spatial frequencies, and progressively lower frequencies... Be aware to not go to high levels if you want to see some details of the input images ! A good compromise for color images is a 0.53 value since such choice won't affect too much the color spectrum. Higher values would lead to gray and blurred output images.

Horizontal cells parameters

This parameter set tunes the neural network connected to the photo-receptors, the horizontal cells. It modulates photo-receptors sensitivity and completes the processing for final spectral whitening (part of the spatial band pass effect thus favoring visual details enhancement).

    horizontalCellsGain here is a critical parameter ! If you are not interested with the mean luminance and want just to focus on details enhancement, then, set this parameterto zero. However, if you want to keep some environment luminance's data, let some low spatial frequencies pass into the system and set a higher value (<1).
    hcellsTemporalConstant similar to photo-receptors, this parameter acts on the temporal constant of a low pass temporal filter that smoothes input data. Here, a high value generates a high retina after effect while a lower value makes the retina more reactive. This value should be lower than photoreceptorsTemporalConstant to limit strong retina after effects.
    hcellsSpatialConstant is the spatial constant of these cells filter's low pass one. It specifies the lowest spatial frequency allowed in what follows. Visually, a high value leads to very low spatial frequencies processing and leads to salient halo effects. Lower values reduce this effect but has the limit of not go lower than the value of photoreceptorsSpatialConstant. Those 2 parameters actually specify the spatial band-pass of the retina.

"""
    
    
def retina_effect(im):
    retina = cv.bioinspired_Retina.create((im.shape[1], im.shape[0]))
    
    # NB: je n'arrive pas a refaire un resultat aussi bon sur le chat que dans l'exemple !
    
    horizontalCellsGain = 0
    horizontalCellsGain = 0.3
    #~ horizontalCellsGain = 0.7
    #~ horizontalCellsGain = 0.
    
    photoreceptorsLocalAdaptationSensitivity = 0.7
    photoreceptorsLocalAdaptationSensitivity = 0.89
    #~ photoreceptorsLocalAdaptationSensitivity = 0.3
    
    ganglionCellsSensitivity = 0.7
    ganglionCellsSensitivity = 0.89
    ganglionCellsSensitivity = 0.3 # more natural
    
    photoreceptorsTemporalConstant  = 0.9
    
    HcellsTemporalConstant = 0.5
    #~ HcellsTemporalConstant = 0.9
    
    retina.setupOPLandIPLParvoChannel(horizontalCellsGain=horizontalCellsGain,photoreceptorsLocalAdaptationSensitivity=photoreceptorsLocalAdaptationSensitivity,ganglionCellsSensitivity=ganglionCellsSensitivity,photoreceptorsTemporalConstant=photoreceptorsTemporalConstant,HcellsTemporalConstant=HcellsTemporalConstant)
    
    print(retina.printSetup())
    
    retina.run(im)
    out = retina.getParvo()
    #~ out = retina.getMagno()
    cv.imshow('retina parvo out', out)
    cv.waitKey(0)
        
#~ acquire_camera()
im = cv2.imread("../alex_pytools/autotest_data/cat_backlight.jpg")
im = cv2.imread("../alex_pytools/autotest_data/HDRtoneMapping_memorialSample.jpg")
retina_effect(im)