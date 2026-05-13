import math
import panda3d

# You can in fact load .obj model files in Panda3D, starting from version 1.10. 
# Just add load-file-type p3assimp to your config.prc file in the etc folder of your Panda3D installation, 
# and you can then load .obj models using model = self.loader.load_model("my_model.obj").

#~ myNodePath = loader.loadModel("path/to/models/myModel.egg")
#~ myModel.reparentTo(render)
#~ myModel.detachNode() # to remove from scene

#cf https://arsthaumaturgis.github.io/Panda3DTutorial.io/tutorial/tut_lesson02.html


import direct
from direct.showbase.ShowBase import ShowBase

from direct.actor.Actor import Actor

from direct.interval.IntervalGlobal import Sequence

from panda3d.core import Point3
from panda3d.core import WindowProperties


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        
        if 0:
            properties = WindowProperties()
            properties.setSize(1400, 750)
            self.win.requestProperties(properties)
        
        # Load the environment model.
        
        if 0:
            self.scene = self.loader.loadModel("models/environment") # load the .egg or the .bam or the egg.pz
            #~ self.scene = self.loader.loadModel("models/misc/camera") 

            for i in range(3):
                print(self.scene.getChild(i))

            # Reparent the model to render.

            self.scene.reparentTo(self.render)

            # Apply scale and position transforms on the model.

            self.scene.setScale(0.25, 0.25, 0.25)

            self.scene.setPos(-8, 42, 0)
        
        # play with the camera position
        self.camera.setPos(0, 0, 32) # change nothing !?!
        self.camera.setP(-90)
        
        #~ self.disableMouse()
        
        if 1:        
            #~ myNodePath = loader.loadModel("MovingWeight_with_roller.stl")
            myNodePath = loader.loadModel("movingweight")
            myNodePath.reparentTo(self.render)
            # myNodePath.detachNode() # to remove from scene
            scale_coef = 10000
            myNodePath.setScale(scale_coef, scale_coef, scale_coef)
            myNodePath.setPos(-8, 7, 0)
            myNodePath.setRenderModeWireframe()
            #~ for i in range(3):
                #~ print(myNodePath.getChild(i))
        
        
        if 0:
            plight = panda3d.core.PointLight('plight')
            plight.setColor((0.2, 0.2, 0.2, 1))
            #~ plight.setColor((10.2, 10.2, 10.2, 1))
            plnp = self.render.attachNewNode(plight)
            plnp.setPos(10, 20, 0)
            self.render.setLight(plnp)
            
            if 1:
                # Use a 512x512 resolution shadow map
                plight.setShadowCaster(True, 512, 512)
                # Enable the shader generator for the receiving nodes
                self.render.setShaderAuto()
            
        if 0:
            # Create Ambient Light
            ambientLight = panda3d.core.AmbientLight('ambientLight')
            ambientLight.setColor((0.1, 0.1, 0.1, 1))
            ambientLightNP = self.render.attachNewNode(ambientLight)
            self.render.setLight(ambientLightNP)
            

        
    

        if 0:
            # Add the spinCameraTask procedure to the task manager.
            self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        # Load and transform the panda actor.

        self.pandaActor = direct.actor.Actor.Actor("models/panda-model",

                                {"walk": "models/panda-walk4"})

        self.pandaActor.setScale(0.005, 0.005, 0.005)

        self.pandaActor.reparentTo(self.render)

        # Loop its animation.

        self.pandaActor.loop("walk")


        if 1:
            # make the panda translates
            
            # Create the four lerp intervals needed for the panda to

            # walk back and forth.

            posInterval1 = self.pandaActor.posInterval(13, # 13s of walk front

                                                       Point3(0, -10, 0),

                                                       startPos=Point3(0, 10, 0))

            posInterval2 = self.pandaActor.posInterval(13,

                                                       Point3(0, 10, 0),

                                                       startPos=Point3(0, -10, 0))

            hprInterval1 = self.pandaActor.hprInterval(3,

                                                       Point3(180, 0, 0),

                                                       startHpr=Point3(0, 0, 0))

            hprInterval2 = self.pandaActor.hprInterval(3,

                                                       Point3(0, 0, 0),

                                                       startHpr=Point3(180, 0, 0))


            # Create and play the sequence that coordinates the intervals.

            self.pandaPace = Sequence(posInterval1, hprInterval1,

                                      posInterval2, hprInterval2,

                                      name="pandaPace")

            self.pandaPace.loop()
            

    def spinCameraTask(self, task):

        angleDegrees = task.time * 6.0

        angleRadians = angleDegrees * (math.pi / 180.0)

        self.camera.setPos(20 * math.sin(angleRadians), -20 * math.cos(angleRadians), 3)

        self.camera.setHpr(angleDegrees, 0, 0)

        return direct.task.Task.cont




def simpleScene():
    app = MyApp()
    app.run()


simpleScene()