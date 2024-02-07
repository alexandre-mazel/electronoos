import math
import panda3d

# You can in fact load .obj model files in Panda3D, starting from version 1.10. 
# Just add load-file-type p3assimp to your config.prc file in the etc folder of your Panda3D installation, 
# and you can then load .obj models using model = self.loader.load_model("my_model.obj").

#~ myNodePath = loader.loadModel("path/to/models/myModel.egg")
#~ myModel.reparentTo(render)
#~ myModel.detachNode() # to remove from scene



from direct.showbase.ShowBase import ShowBase
from direct.task import Task


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        
        # Load the environment model.

        self.scene = self.loader.loadModel("models/environment")

        # Reparent the model to render.

        self.scene.reparentTo(self.render)

        # Apply scale and position transforms on the model.

        self.scene.setScale(0.25, 0.25, 0.25)

        self.scene.setPos(-8, 42, 0)
        
        myNodePath = loader.loadModel("MovingWeight_with_roller.stl")
        myNodePath.reparentTo(self.render)
        myNodePath.detachNode() # to remove from scene
        myNodePath.setScale(10., 10., 10.)
        
        # Add the spinCameraTask procedure to the task manager.

        if 1:
            # start spin task
            self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")


    # Define a procedure to move the camera.

    def spinCameraTask(self, task):

        angleDegrees = task.time * 6.0

        angleRadians = angleDegrees * (math.pi / 180.0)

        self.camera.setPos(20 * math.sin(angleRadians), -20 * math.cos(angleRadians), 3)

        self.camera.setHpr(angleDegrees, 0, 0)

        return Task.cont




def simpleScene():
    app = MyApp()
    app.run()


simpleScene()