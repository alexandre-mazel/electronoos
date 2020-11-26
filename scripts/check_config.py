def checkOpenCV():
    import cv2
    print("cv2: %s" % str(cv2.__version__) )
    try:
        dir(cv2.dnn)
        print("cv2: dnn found" )
    except:
        print("cv2: dnn NOT OK" )
        



def checkTensorFlow():
    import tensorflow as tf
    try:
        tf.__version__ = tf.version.VERSION
    except: pass
    print("tf: %s" % str( tf.__version__ ) )
    
    
checkOpenCV()    
checkTensorFlow()

# cat /usr/local/cuda/version.txt