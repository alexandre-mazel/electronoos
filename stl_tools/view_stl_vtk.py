import vtk # pip install vtk # tested with vtk-9.3.0-cp39-cp39-win_amd64.whl
import sys

from vtkmodules.vtkRenderingCore import vtkRenderer

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
        
def showStl(filename, bAnimate=True, bDrawingTechnic = True):
    
    class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

        def __init__(self,parent=None):
            self.parent = renderWindowInteractor

            self.AddObserver("KeyPressEvent",self.keyPressEvent)

        def keyPressEvent(self,obj,event):
            key = self.parent.GetKeySym()
            print("DBG: keyPressEvent: key: %s" % key)
            if key == 'Escape':
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
    renderWindow.SetSize(768,768)
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
        rots =  (
                        (0,0,0),
                        (0,90,0),
                        (90,0,0),
                        (30,-35,0),
                    )
        rBackgroundColor = 0.9
        for i in range(4):
            ren = vtkRenderer()
            renderWindow.AddRenderer(ren)
            ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])
            ren.AddActor(actors[i])
            actors[i].RotateX(rots[i][0])
            actors[i].RotateY(rots[i][1])
            actors[i].RotateZ(rots[i][2])
            ren.SetBackground(rBackgroundColor, rBackgroundColor, rBackgroundColor)
            
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
    
    if bDrawingTechnic:
        outfn = filename.lower().replace(".stl","_tech.") + "png"
        WriteImage(outfn, renderWindow, rgba=True)
        # todo: write cartouche in 2nd pass using opencv2 !!!


if __name__ == "__main__":
    fn = "MovingWeight_with_roller.stl"
    #~ fn = "CameraFishEye_p1.stl"
    fn = "CameraFishEye_p2.stl"
    fn = "gaia_logo.stl"
    if len(sys.argv)>1:
        fn = sys.argv[1]
    showStl(fn,bDrawingTechnic=1)