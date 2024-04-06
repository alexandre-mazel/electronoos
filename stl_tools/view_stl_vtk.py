import datetime
import os
import sys
import time

import vtk # pip install vtk # tested with vtk-9.3.0-cp39-cp39-win_amd64.whl

def getElectronoosPath():
    if os.name == "nt":
        strElectroPath = "C:/Users/alexa/dev/git/electronoos/"
        if not os.path.isdir(strElectroPath):
            strElectroPath = "c:/dev/git/electronoos/"
    else:
        if os.path.expanduser("~") == "/var/www": # from modpython
            strElectroPath = os.path.expanduser("/home/na/dev/git/electronoos/")
        else:
            strElectroPath = os.path.expanduser("~/dev/git/electronoos/")
            strElectroPath = os.path.expanduser("/home/na/dev/git/electronoos/") # when started in root
    return strElectroPath
        
sys.path.append(getElectronoosPath()+"alex_pytools/")
import cv2_tools

from vtkmodules.vtkRenderingCore import vtkRenderer

def getDate( timeepoch = -1 ):
    """
    return a string describing in french the date.
    - timeepoch: if -1: return now
    """
    if timeepoch == -1:
        timeepoch = time.time()
    datetimeObject = datetime.datetime.fromtimestamp(timeepoch)
    strStamp = datetimeObject.strftime( "%d %b %Y") # %B or %b
    return strStamp

def WriteCartouche(filename_generated, filename_original, nbr_faces = 0):
    """
    Add cartouche to the image in filename_generated.
    Info are related to filename_original (the stl)
    """
    print("INF: WriteCartouche: Writing to '%s'" % filename_generated)
    import cv2
    im = cv2.imread(filename_generated,cv2.IMREAD_UNCHANGED) # handle RGBA
    
    black = (0,0,0,255)
        
    hi,wi = im.shape[:2]
    
    # image separators
    cv2.line( im, (0,hi//2), (wi,hi//2), black, 1 )
    cv2.line( im, (wi//2,0), (wi//2,hi), black, 1 )

    
    # image border
    cv2.line( im, (0,0), (wi,0), black, 1 )
    cv2.line( im, (0,hi-1), (wi,hi-1), black, 1 )
    cv2.line( im, (0,0), (0,hi-1), black, 1 )
    cv2.line( im, (wi-1,0), (wi-1,hi-1), black, 1 )
    
    """
    ------------------------------------------
    | repr logo  |                   | date stl
    _________ | piece name  |
    | Stl           |                   | date render
    """
    wCart = 200
    hCart = 80
    leCart = wi-wCart-1 # -1 for the border
    toCart = hi-hCart-1

    
    font           = cv2.FONT_HERSHEY_SIMPLEX
    fontScale   = 1
    fontColor   = (0,0,0,255) # 255 for alpha, else it's not visible in the output
    thickness   = 2
    lineType     = 2
    
    #~ cv2.line( im, (leCart,toCart), (wi,toCart), black, 1 )
    #~ cv2.line( im, (leCart,toCart), (leCart,hi), black, 1 )
    
    global nRotationConfig
    text1 = ["Front","Right","Top"]
    text2 = ["Front","Right","Bottom"]
    text3 = ["Front","Right","Bottom"]
    titless = [text1,text2,text3]
    titles = titless[nRotationConfig%len(titless)]
    
    if 1:
        # puttext front left ...
        margin = 20
        hmargin = margin+20
        cv2.putText( im, titles[0],  ( 0+margin, 0+hmargin ), font, 1, fontColor, 1 ) #todo: write a '*' beside the name if camera or object has been moved!
        cv2.putText( im, titles[1],  ( 0+margin+wi//2, 0+hmargin ), font, 1, fontColor, 1 )
        cv2.putText( im, titles[2],  ( 0+margin, 0+hmargin+hi//2 ), font, 1, fontColor, 1 )

    strDateFile = getDate(os.path.getmtime(filename_original))
    strDateNow = getDate()
    
    strName = os.path.basename(filename_original).replace(".stl","")
    
    nSize = os. path. getsize(filename_original)
    strInfo = "Format: STL, size: %dkB" % (nSize/1024) 
    
    
    nbrTotalLine = 5
    line = 0
    if nbr_faces > 0:
        nbrTotalLine += 1
        
    cv2_tools.putTextBox( im, strName,  (leCart,toCart,leCart+wCart,toCart+hCart*2//nbrTotalLine), font, fontColor, thickness, bOutline=0, bRenderBox=1 ); line += 2
    
    if nbr_faces > 0:
        cv2_tools.putTextBox( im, "Nbr Triangle: " + str(nbr_faces),  (leCart,toCart+hCart*line//nbrTotalLine,leCart+wCart,toCart+hCart*(line+1)//nbrTotalLine), font, fontColor, thickness//2, bOutline=0, bRenderBox=1 ); line += 1
    
    cv2_tools.putTextBox( im, strInfo,  (leCart,toCart+hCart*line//nbrTotalLine,leCart+wCart,toCart+hCart*(line+1)//nbrTotalLine), font, fontColor, thickness//2, bOutline=0, bRenderBox=1 ); line += 1
    cv2_tools.putTextBox( im, "File : " + strDateFile,  (leCart,toCart+hCart*line//nbrTotalLine,leCart+wCart,toCart+hCart*(line+1)//nbrTotalLine), font, fontColor, thickness//2, bOutline=0, bRenderBox=1 ); line += 1
    cv2_tools.putTextBox( im, "Render: " + strDateNow,  (leCart,toCart+hCart*line//nbrTotalLine,leCart+wCart,toCart+hCart*(line+1)//nbrTotalLine), font, fontColor, thickness//2, bOutline=0, bRenderBox=1 ); line += 1
    cv2.imwrite( filename_generated, im )
    if 1:
        cv2.imshow("cartouche", im)
        cv2.waitKey(0)
    

def WriteImage(fileName, renWin, rgba=True):
    '''
    Write the render window view to an image file.

    Image types supported are:
     BMP, JPEG, PNM, PNG, PostScript, TIFF.
    The default parameters are used for all writers, change as needed.

    :param fileName: The file name, if no extension then PNG is assumed.
    :param renWin: The render window.
    :param rgba: Used to set the buffer type.
    :return:
    '''

    import os
    from vtkmodules.vtkIOImage import (
        vtkBMPWriter,
        vtkJPEGWriter,
        vtkPNGWriter,
        vtkPNMWriter,
        vtkPostScriptWriter,
        vtkTIFFWriter
    )
    
    from vtkmodules.vtkRenderingCore import (
        vtkWindowToImageFilter
    )

    # Select the writer to use.
    path, ext = os.path.splitext(fileName)
    ext = ext.lower()
    if not ext:
        ext = '.png'
        fileName = fileName + ext
    if ext == '.bmp':
        writer = vtkBMPWriter()
    elif ext == '.jpg':
        writer = vtkJPEGWriter()
    elif ext == '.pnm':
        writer = vtkPNMWriter()
    elif ext == '.ps':
        if rgba:
            rgba = False
        writer = vtkPostScriptWriter()
    elif ext == '.tiff':
        writer = vtkTIFFWriter()
    else:
        writer = vtkPNGWriter()

    windowto_image_filter = vtkWindowToImageFilter()
    windowto_image_filter.SetInput(renWin)
    windowto_image_filter.SetScale(1)  # image quality
    if rgba:
        windowto_image_filter.SetInputBufferTypeToRGBA()
    else:
        windowto_image_filter.SetInputBufferTypeToRGB()
        # Read from the front buffer.
        windowto_image_filter.ReadFrontBufferOff()
        windowto_image_filter.Update()

    writer.SetFileName(fileName)
    writer.SetInputConnection(windowto_image_filter.GetOutputPort())
    writer.Write()
    print("INF: WriteImage: rendered image written to '%s'" % fileName)
    
bRenderToFile = False      
nRotationConfig = 0

def showStl(filename, bAnimate=True, bDrawingTechnic = True):
    
    class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

        def __init__(self,parent=None):
            self.parent = renderWindowInteractor

            self.AddObserver("KeyPressEvent",self.keyPressEvent)

        def keyPressEvent(self,obj,event):
            key = self.parent.GetKeySym()
            print("DBG: keyPressEvent: key: %s" % key)
            
            bExit = False
            if key == 'p' or key == 't' or key == 'd': # for Print or Technical Drawing
                global bRenderToFile
                bRenderToFile = True
                print("rendering to file then Exiting!")
                bExit = True
                
            if key == 'r' or key == 'f': # for Rotate or Flip
                global nRotationConfig
                nRotationConfig += 1
                print("INF: rotation config is now: " + str(nRotationConfig))
                #~ callback_func_animate(None,None)
                showStl(filename,bAnimate=False,bDrawingTechnic=True)
                bExit = True
                
            if key == 'Escape':
                bExit = True
                
            if bExit:
                print("Exiting!")
                renderWindow.Finalize()
                self.parent.TerminateApp()
            return
            
        
    def callback_func_animate(caller, timer_event):
        actor.RotateX(1)
        actor.RotateY(0.35)
        actor.RotateZ(0.13)
        renderWindow.Render()
        
    # Create a reader
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)

    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
        
    #actor.SetPosition(0,0,0)
    # put the center at the center of the world!
    center = actor.GetCenter()
    actor.SetOrigin(center)
    #~ actor.RotateX(30)
    #~ actor.RotateY(30)
    #~ actor.RotateZ(30)

    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(1024,1024)
    renderWindow.SetWindowName(filename)

    renderWindow.AddRenderer(renderer)

    # An interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)


    # Add the actors to the scene
    renderer.AddActor(actor)
    rBackgroundColor = 0.75
    renderer.SetBackground(rBackgroundColor, rBackgroundColor, rBackgroundColor)
    

    # Render and interact
    renderWindow.Render()
    
    # WriteImage("test", renderWindow, rgba=False)
    
    if bDrawingTechnic:
        bAnimate = False
        actors = []
        for i in range(3):
            actorNew = vtk.vtkActor()
            actorNew.SetMapper(mapper)
            actors.append(actorNew)
        actors.append(actor)
        #~ actor2.SetPosition(100,100,0)
        #~ renderer.AddActor(actor2)
        # simpler way: write 4 images into 4 different file, then paste them
        
        #viewports:
        # Define viewport ranges.
        xmins = [0, .5, 0, .5]
        xmaxs = [0.5, 1, 0.5, 1]
        ymins = [.5, .5, 0, 0]
        ymaxs = [1, 1,0.5, 0.5]
        # sympa pour des impressions a plat genre le logo gaia
        rots1 =  (
                        (0,0,0),
                        (0,90,0),
                        (-90,0,0),
                        (30,-35,0),
                    )
        # plus respectueux de la maniere de les dessiner (par exemple scene des cuves du louvres)
        rots2 =  (
                (-90,0,0),
                (-90,0,-90),
                (0,0,0),      # (180,0,0),
                (-40,0,-20),
            )
            
        rots3 =  (
                (-90,0,0),
                (-90,0,-90),
                (180,0,0),
                (-40,0,-20),
            )
            
        rotsConfig = [rots2,rots3, rots1]
        rots = rotsConfig[nRotationConfig%len(rotsConfig)]
        rBackgroundColor = 0.8
        for i in range(4):
            ren = vtkRenderer()
            renderWindow.AddRenderer(ren)
            ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])
            ren.AddActor(actors[i])
            # order matters
            actors[i].RotateX(rots[i][0])
            actors[i].RotateY(rots[i][1])
            actors[i].RotateZ(rots[i][2])
            ren.SetBackground(rBackgroundColor, rBackgroundColor, rBackgroundColor)
            if i < 3:
                # flat mode
                actors[i].GetProperty().SetColor(0.9,0.9,0.9)
                # next lines change nothing
                actors[i].GetProperty().SetRepresentationToSurface()
                actors[i].GetProperty().EdgeVisibilityOff()
                actors[i].GetProperty().SetEdgeColor(0,1,0)
                actors[i].GetProperty().SetLineWidth(1.5)
                pass
            else:
                # shaded mode
                # just getting the activecamera change it!
                #~ cam = ren.GetActiveCamera()
                #~ print(cam.GetFocalPoint())
                #~ cam.SetFocalPoint(0.,0.,0.)
                #~ cam.SetPosition(0.,0.,0.)
                actor.GetProperty().SetColor(0.5,0.5,1)
                
            
        # try to add text (not working)
        txtActor = vtk.vtkActor2D()
        txtMapper = vtk.vtkTextMapper()
        txtActor.SetMapper(txtMapper)
        
        txt = vtk.vtkTextActor()
        txt.SetInput(filename)
        txtprop = txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(18)
        txt.SetTextProperty(txtprop)
        txtprop.SetColor(1,1,1)
        txt.SetDisplayPosition(0,0)
        ren.AddActor2D(txt)
        
        textrepresentation = vtk.vtkTextRepresentation()
        textrepresentation.GetPositionCoordinate().SetCoordinateSystem(3)
        textwidget = vtk.vtkTextWidget()
        textwidget.SetRepresentation(textrepresentation)
        textwidget.SetTextActor(txt)
        textwidget.SelectableOff()
        textwidget.ResizableOff() 
        #~ textwidget.On()
            
        
    # bDrawingTechnic
    
            
    # another test of txt (not working either)
    if 0:
        #~ from vtkmodules.vtkInteractionWidgets import (
        #~ vtkTextRepresentation,
        #~ vtkTextWidget
        #~ )
        #~ from vtkmodules.vtkRenderingCore import (
            #~ vtkActor,
            #~ vtkPolyDataMapper,
            #~ vtkRenderWindow,
            #~ vtkRenderWindowInteractor,
            #~ vtkRenderer,
            #~ vtkTextActor
        #~ )

        # Create the TextActor
        text_actor = vtkTextActor()
        text_actor.SetInput('This is a test')
        text_actor.GetTextProperty().SetColor(1,1,1)

        # Create the text representation. Used for positioning the text_actor
        text_representation = vtkTextRepresentation()
        text_representation.GetPositionCoordinate().SetValue(0.15, 0.15)
        text_representation.GetPosition2Coordinate().SetValue(0.7, 0.2)

        # Create the TextWidget
        # Note that the SelectableOff method MUST be invoked!
        # According to the documentation :
        #
        # SelectableOn/Off indicates whether the interior region of the widget can be
        # selected or not. If not, then events (such as left mouse down) allow the user
        # to 'move' the widget, and no selection is possible. Otherwise the
        # SelectRegion() method is invoked.
        text_widget = vtkTextWidget()
        text_widget.SetRepresentation(text_representation)

        text_widget.SetInteractor(renderer.AddActor(actor))
        text_widget.SetTextActor(text_actor)
        text_widget.SelectableOff()
        
        text_widget.On()
        #~ renderWindow.Render()
    
    if bAnimate:
        # animate
        renderWindowInteractor.Initialize()
        refresh_rate = 25 # ms
        renderWindowInteractor.CreateRepeatingTimer(int(refresh_rate))
        renderWindowInteractor.AddObserver("TimerEvent", callback_func_animate)
        
    # keyboard interaction
    renderWindowInteractor.SetInteractorStyle(MyInteractorStyle())
    
    renderWindowInteractor.Start()
    print("bRenderToFile: %s" % bRenderToFile )
    if bRenderToFile:
        print("INF: Rendering to file...")
        print("actor rot: %s" % str(actor.GetOrientationWXYZ()) )
        outfn = filename.lower().replace(".stl","__technical_drawing.") + "png"
        WriteImage(outfn, renderWindow, rgba=True)
        
        nbr_faces = 0
        #~ nbr_faces = actor.GetMapper().GetNumberOfFaces()
        
        WriteCartouche( outfn, filename, nbr_faces = nbr_faces )
        # todo: write cartouche in 2nd pass using opencv2 !!!
        exit(3)


if __name__ == "__main__":
    """
    
    """
    print("Syntaxe: <scriptname> <stl_file>")
    print("during rendering:")
    print( "\tpress 'p', 't' or 'd' to render to a file then exit")
    print( "\tpress 'r' to rotate one config")
    fn = "MovingWeight_with_roller.stl"
    #~ fn = "CameraFishEye_p1.stl"
    fn = "CameraFishEye_p2.stl"
    fn = "gaia_logo.stl"
    fn = "spool_test.stl"
    if 0:
        WriteCartouche("gaia_logo_technical_drawing.png","gaia_logo.stl",123)
        exit(2)

    if len(sys.argv)>1:
        fn = sys.argv[1]
    showStl(fn,bDrawingTechnic=1)