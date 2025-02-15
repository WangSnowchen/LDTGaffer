import IECore

import Gaffer
import GafferArnold
import GafferScene
import imath

# \todo Nice geometry


class LDTShaderBallScene(GafferScene.SceneNode):
    def __init__(self, name="LDTShaderBallScene"):

        GafferScene.SceneNode.__init__(self, name)

        # Public plugs

        self["shader"] = GafferScene.ShaderPlug()
        self["resolution"] = Gaffer.IntPlug(defaultValue=512, minValue=0)

        #Gaffer.Metadata.registerValue(self["scene"], "nodule:type", "")
        #Gaffer.Metadata.registerValue(
        #    self["scene"], "plugValueWidget:type", "GafferUI.PresetsPlugValueWidget"
        #)
        #Gaffer.Metadata.registerValue(self["scene"], "preset:shaderBall", 0)
        #Gaffer.Metadata.registerValue(self["scene"], "preset:customGeo", 1)

        # Private internal network



        # Camera        
        self["__camera"] = GafferScene.Camera()
        self["__camera"]["transform"]["translate"].setValue(imath.V3f(0, 86, 225))
        self["__camera"]["transform"]["rotate"].setValue(imath.V3f(-16, 0, 0))
        self["__camera"]["fieldOfView"].setValue(20.0)

        # Env
        self["__envMapFilename"] = Gaffer.StringPlug(
            defaultValue="${GAFFER_ROOT}/resources/hdri/studio.exr"
        )

        # SkyDome
        self["__envMap"] = GafferArnold.ArnoldShader()
        self["__envMap"].loadShader("image")
        self["__envMap"]["parameters"]["filename"].setInput(self["__envMapFilename"])

        self["__skyDome"] = GafferArnold.ArnoldLight()
        self["__skyDome"].loadShader("skydome_light")
        self["__skyDome"]["parameters"]["color"].setInput(self["__envMap"]["out"])
        self["__skyDome"]["parameters"]["format"].setValue("latlong")

        # Expose Plugs
        self.addChild(
           self["__skyDome"]["parameters"]["exposure"].createCounterpart(
               "exposure", Gaffer.Plug.Direction.In
           )
        )
        self["__skyDome"]["parameters"]["exposure"].setInput(self["exposure"])

        # Join ShaderBall and Camera
        self["__parent"] = GafferScene.Parent()
        #self["__parent"]["in"].setInput(self["__shaderBallReference"]["out"])
        self["__parent"]['children']['child0'].setInput(self["__camera"]["out"])
        self["__parent"]['children']['child1'].setInput(self["__skyDome"]["out"])
        self["__parent"]["parent"].setValue("/")


        self["__shaderAssignment"] = GafferScene.ShaderAssignment()
        self["__shaderAssignment"]["in"].setInput(self["__parent"]["out"])
        self["__shaderAssignment"]["shader"].setInput(self["shader"])
        self["__shaderAssignmentFilter"] = GafferScene.SetFilter("SetFilter")
        self["__shaderAssignmentFilter"]["setExpression"].setValue(
            "ShaderBall:material"
        )

        self["__shaderAssignment"]["filter"].setInput(
            self["__shaderAssignmentFilter"]["out"]
        )

        # Standard Options

        self["__options"] = GafferScene.StandardOptions()
        self["__options"]["in"].setInput(self["__shaderAssignment"]["out"])

        self["__options"]["options"]["renderCamera"]["enabled"].setValue(True)
        self["__options"]["options"]["renderCamera"]["value"].setValue("/camera")
        self["__options"]["options"]["renderResolution"]["enabled"].setValue(True)
        # Expose Plugs
        self["__options"]["options"]["renderResolution"]["value"][0].setInput(
            self["resolution"]
        )
        self["__options"]["options"]["renderResolution"]["value"][1].setInput(
            self["resolution"]
        )

        # Arnold Options
        self["__arnoldOptions"] = GafferArnold.ArnoldOptions()
        self["__arnoldOptions"]["in"].setInput(self["__options"]["out"])
        self["__arnoldOptions"]["options"]["aaSamples"]["enabled"].setValue(True)
        self["__arnoldOptions"]["options"]["aaSamples"]["value"].setValue(3)
        # Expose Plugs
        self.addChild(
            self["__arnoldOptions"]["options"]["threads"].createCounterpart(
                "threads", Gaffer.Plug.Direction.In
            )
        )
        self["__arnoldOptions"]["options"]["threads"].setInput(self["threads"])

        self["__emptyScene"] = GafferScene.ScenePlug()
        self["__enabler"] = Gaffer.Switch()
        self["__enabler"].setup(GafferScene.ScenePlug())
        self["__enabler"]["in"][0].setInput(self["__emptyScene"])
        self["__enabler"]["in"][1].setInput(self["__arnoldOptions"]["out"])
        self["__enabler"]["enabled"].setInput(self["enabled"])
        self["__enabler"]["index"].setValue(1)

        self["out"].setFlags(Gaffer.Plug.Flags.Serialisable, False)
        self["out"].setInput(self["__enabler"]["out"])

    # Internal plug which the final scene is connected into.
    # Derived classes may insert additional nodes between this
    # plug and its input to modify the scene.
    def _inPlug(self):

        return self["__parent"]["in"]


IECore.registerRunTimeTyped(LDTShaderBallScene, typeName="GafferScene::LDTShaderBallScene")
