import vtk # pip install vtk # tested with vtk-9.3.0-cp39-cp39-win_amd64.whl

def main():
    # Create a reader
    reader = vtk.vtkSTLReader()
    reader.SetFileName("MovingWeight_with_roller.stl")

    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
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
    renderWindowInteractor.Start()

if __name__ == "__main__":
    main()