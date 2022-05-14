from pxr import Usd, Sdf, UsdGeom

cube = """#usda 1.0
def Xform "geo"
{
    def Cube "cube"
    {
    }
}"""
sphere = """#usda 1.0
def Xform "geo"
{
    def Sphere "sphere"
    {
    }
}"""


def MakeLayer(filename, text):
    l = Sdf.Layer.CreateNew(filename)
    l.ImportFromString(text)
    return l


defaultlayer = MakeLayer("cube.usda", cube)
stage = Usd.Stage.Open(defaultlayer)
stage.GetRootLayer().Save()
defaultlayer = MakeLayer("sphere.usda", sphere)
stage = Usd.Stage.Open(defaultlayer)
stage.GetRootLayer().Save()
# print(defaultlayer.defaultPrim, defaultlayer.rootPrims)
# stage = Usd.Stage.CreateNew('HelloWorld.usda')
# print(prim)
# stage.SetDefaultPrim(defaultlayer.pseudoRoot)

# UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
