import vtk # pip install vtk # tested with vtk-9.3.0-cp39-cp39-win_amd64.whl

def showStl(filename):
    
        
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
    
    # animate
    renderWindowInteractor.Initialize()
    refresh_rate = 25 # ms
    renderWindowInteractor.CreateRepeatingTimer(int(refresh_rate))
    renderWindowInteractor.AddObserver("TimerEvent", callback_func_animate)

    # Render and interact
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
    showStl("MovingWeight_with_roller.stl")