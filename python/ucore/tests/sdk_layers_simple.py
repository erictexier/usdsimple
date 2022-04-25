import os, platform, itertools, sys, unittest

# to keep in mind
# preferredResolver = os.environ.get(
#     "TEST_SDF_LAYER_RESOLVER", "Sdf_TestResolver")
# from pxr import Ar
# Ar.SetPreferredResolver(preferredResolver)

# to keep in mind
# from pxr import Tf
# Tf.Notice.RegisterGlobally
# with self.assertRaises(Tf.ErrorException):


from pxr import Sdf, Tf, Plug, Usd, UsdGeom, Kind
FILENAME = "testLayersave.usda"

class DefaultUtilsUsd(object):
    @staticmethod
    def default_empty(filename, withprim=False):
        emptyL = Sdf.Layer.CreateNew(filename, args={"format": "usda"})
        if withprim:
            emptyStage = Usd.Stage.Open(emptyL)
            emptyPrim = UsdGeom.Xform.Define(emptyStage, "/").GetPrim()
            emptyStage.SetDefaultPrim(emptyPrim)
        Usd.Stage.Open(emptyL).GetRootLayer().Save()

    @staticmethod
    def default_root(filename):
        emptyL = Sdf.Layer.CreateNew(filename, args={"format": "usda"})
        layers = emptyL.subLayerPaths
        layers.append("sublayer_1.usda")
        Usd.Stage.Open(emptyL).GetRootLayer().Save()

    @staticmethod
    def default_sphere(filename):
        sphereL = Sdf.Layer.CreateNew(filename, args={"format": "usda"})
        stage = Usd.Stage.Open(sphereL)
        #stage.SetDefaultPrim(xform_prim)
        xform_prim = UsdGeom.Xform.Define(stage, '/hello')
        # stage.SetDefaultPrim(xform_prim)
        sphere_prim = UsdGeom.Sphere.Define(stage, '/hello/world')

        Usd.Stage.Open(sphereL).GetRootLayer().Save()

class CtxCreate(object):
    filename = FILENAME
    sublayers = ["./temp/sublayer_1.usda", "./temp/sublayer_2.usda"]
    references = ["./temp/ref_1.usda", "./temp/ref_2.usda"]
    payloads = ["./temp/payload_1.usda", "./temp/payload_2.usda"]


'''
    def _AddModelRef(self, stage, path, refPath):
        """
        Adds a reference to refPath at the given path in the stage.  This will make
        sure the model hierarchy is maintained by ensuring that all ancestors of
        the path have "kind" set to "group".

        returns the referenced model.
        """

        from pxr import Kind, Sdf, Usd, UsdGeom

        # convert path to an Sdf.Path which has several methods that are useful
        # when working with paths.  We use GetPrefixes() here which returns a list
        # of all the prim prefixes for a given path.
        path = Sdf.Path(path)
        # print path
        # print path.GetPrefixes()
        for prefixPath in path.GetPrefixes()[1:-1]:
            parentPrim = stage.GetPrimAtPath(prefixPath)
            if not parentPrim:
                parentPrim = UsdGeom.Xform.Define(stage, prefixPath).GetPrim()
                Usd.ModelAPI(parentPrim).SetKind(Kind.Tokens.group)

        # typeless def here because we'll be getting the type from the prim that
        # we're referencing.
        m = stage.DefinePrim(path)
        m.GetReferences().AddReference(refPath)
        return m
'''



class RootUtilsUsd(DefaultUtilsUsd):
    SubLayer = list()
    def __init__(self):
        pass

    def build_sublayer(self, ctx):
        result_layer = Sdf.Layer.CreateNew(ctx.filename, args={"format": "usda"})
        layers = result_layer.subLayerPaths

        # a list of existing file
        sublayer_filenames = CtxCreate.sublayers
        # assert len(self.SubLayer) == len(sublayer_filenames)
        for afile in sublayer_filenames:
            layers.append(afile)
        return result_layer

    def add_references(self, prim, ctx):
        """Will create the refs, not updating them"""
        reference_filenames = ctx.references
        for afile in reference_filenames:
            referencedStage = Usd.Stage.CreateNew(afile)
            referencedAssetPrim = referencedStage.DefinePrim(prim.GetPath())
            referencedStage.SetDefaultPrim(referencedAssetPrim)
            referencedStage.GetRootLayer().Save()
            prim.GetReferences().AddReference(afile)


    def add_payloads(self, stage, prim, rpath, ctx):
        """Will create the refs, not updating them"""
        # path = Sdf.Path(rpath)
        # for prefixPath in path.GetPrefixes()[1:-1]:
        #     parentPrim = stage.GetPrimAtPath(prefixPath)
        #     print(prefixPath, parentPrim)
        #     if not parentPrim:
        #         parentPrim = UsdGeom.Xform.Define(stage, prefixPath).GetPrim()
        #         Usd.ModelAPI(parentPrim).SetKind(Kind.Tokens.group)
        payload_filenames = ctx.payloads
        for afile in payload_filenames:
            payloadStage = Usd.Stage.CreateNew(afile)
            payloadAssetPrim = payloadStage.DefinePrim(prim.GetPath())
            payloadStage.SetDefaultPrim(payloadAssetPrim)
            payloadStage.GetRootLayer().Save()
            prim.GetPayloads().AddPayload(afile)



class TestTop(unittest.TestCase):

    def test_UpdateCompositionAssetDependency(self):
        asset_stage = None
        if 1:
            assetname = "paul"
            ctx_create = CtxCreate

            # build external files
            defaultfiles = CtxCreate.sublayers
            # + CtxCreate.references + CtxCreate.payloads
            for afile in defaultfiles[:-1]:
                DefaultUtilsUsd.default_empty(afile)
            DefaultUtilsUsd.default_sphere(defaultfiles[-1])
            top = RootUtilsUsd()

            # create a layer with all the sublayer
            src_layer =  top.build_sublayer(ctx_create)

            asset_stage = Usd.Stage.Open(src_layer)
            # prim
            rpath = "/%s" % assetname
            asset_prim = UsdGeom.Xform.Define(asset_stage, rpath).GetPrim()
            asset_stage.SetDefaultPrim(asset_prim)
            UsdGeom.SetStageUpAxis(asset_stage, UsdGeom.Tokens.y)

            model = Usd.ModelAPI(asset_prim)
            model.SetKind(Kind.Tokens.component)
            
            model.SetAssetName(assetname)
            model.SetAssetIdentifier('.temp/%s.usda' %  assetname)

            rpath2 = "/%s/foo1/foo2/foo3" % assetname 
            top.add_references(asset_prim, ctx_create)
            top.add_payloads(asset_stage, asset_prim, rpath2, ctx_create)

        else:
            srcLayer = Sdf.Layer.CreateAnonymous()

        srcLayerStr = '''\
#usda 1.0
(
    subLayers = [
        @sublayer_1.usda@,
        @sublayer_2.usda@
    ]
)

def "Root" (
    payload = @payload_1.usda@
    references = [
        @ref_1.usda@,
        @ref_2.usda@
    ]
)
{
    def "Child" (
        payload = @payload_1.usda@
        references = [
            @ref_1.usda@,
            @ref_2.usda@
        ]
    )
    {
    }

    variantSet "v" = {
        "x" (
            payload = [
                @payload_1.usda@, 
                @payload_2.usda@
            ]
            references = [
                @ref_1.usda@,
                @ref_2.usda@
            ]
        ) {
            def "ChildInVariant" (
                payload = [
                    @payload_1.usda@, 
                    @payload_2.usda@
                ]
                references = [
                    @ref_1.usda@,
                    @ref_2.usda@
                ]
            )
            {
            }
        }
    }
}
        '''
        # srcLayer.ImportFromString(srcLayerStr)
        # Calling UpdateCompositionAssetDependency with an empty old layer path
        # is not allowed.
        #origLayer = srcLayer.ExportToString()
        # srcLayer.Export("testLayersave.sdf")
        if asset_stage:
             asset_stage.GetRootLayer().Save()
        return
        self.assertFalse(srcLayer.UpdateCompositionAssetDependency("", ""))
        self.assertEqual(origLayer, srcLayer.ExportToString())

        # Calling UpdateCompositionAssetDependency with an asset path that does
        # not exist should result in no changes to the layer.
        self.assertTrue(srcLayer.UpdateCompositionAssetDependency(
            "nonexistent.sdf", "foo.sdf"))
        self.assertEqual(origLayer, srcLayer.ExportToString())

        # Test renaming / removing sublayers.
        self.assertTrue(srcLayer.UpdateCompositionAssetDependency(
            "sublayer_1.sdf", "new_sublayer_1.sdf"))
        self.assertEqual(
            srcLayer.subLayerPaths, ["new_sublayer_1.sdf", "sublayer_2.sdf"])

        self.assertTrue(srcLayer.UpdateCompositionAssetDependency(
            "sublayer_2.sdf", ""))
        self.assertEqual(srcLayer.subLayerPaths, ["new_sublayer_1.sdf"])

        # Test renaming / removing payloads.
        primsWithReferences = [
            srcLayer.GetPrimAtPath(p) for p in
            ["/Root", "/Root/Child", "/Root{v=x}", "/Root{v=x}ChildInVariant"]
        ]
        primsWithSinglePayload = [
            srcLayer.GetPrimAtPath(p) for p in
            ["/Root", "/Root/Child"]
        ]
        primsWithPayloadList = [
            srcLayer.GetPrimAtPath(p) for p in
            ["/Root{v=x}", "/Root{v=x}ChildInVariant"]
        ]

        self.assertTrue(srcLayer.UpdateCompositionAssetDependency(
            "payload_1.sdf", "new_payload_1.sdf"))
        for prim in primsWithSinglePayload:
            self.assertEqual(
                prim.payloadList.explicitItems, 
                [Sdf.Payload("new_payload_1.sdf", "/Payload")],
                "Unexpected payloads {0} at {1}".format(prim.payloadList, prim.path))
        for prim in primsWithPayloadList:
            self.assertEqual(
                prim.payloadList.explicitItems, 
                [Sdf.Payload("new_payload_1.sdf", "/Payload"),
                 Sdf.Payload("payload_2.sdf", "/Payload2")],
                "Unexpected payloads {0} at {1}".format(prim.payloadList, prim.path))

        self.assertTrue(srcLayer.UpdateCompositionAssetDependency(
            "new_payload_1.sdf", ""))
        for prim in primsWithSinglePayload:
            self.assertEqual(
                prim.payloadList.explicitItems, [],
                "Unexpected payloads {0} at {1}".format(prim.payloadList, prim.path))
        for prim in primsWithPayloadList:
            self.assertEqual(
                prim.payloadList.explicitItems, 
                [Sdf.Payload("payload_2.sdf", "/Payload2")],
                "Unexpected payloads {0} at {1}".format(prim.payloadList, prim.path))

        # Test renaming / removing references.
        self.assertTrue(srcLayer.UpdateCompositionAssetDependency(
            "ref_1.sdf", "new_ref_1.sdf"))
        for prim in primsWithReferences:
            self.assertEqual(
                prim.referenceList.explicitItems,
                [Sdf.Reference("new_ref_1.sdf", "/Ref"),
                 Sdf.Reference("ref_2.sdf", "/Ref2")],
                "Unexpected references {0} at {1}"
                .format(prim.referenceList, prim.path))

        self.assertTrue(srcLayer.UpdateCompositionAssetDependency(
            "ref_2.sdf", ""))
        for prim in primsWithReferences:
            self.assertEqual(
                prim.referenceList.explicitItems,
                [Sdf.Reference("new_ref_1.sdf", "/Ref")],
                "Unexpected references {0} at {1}"
                .format(prim.referenceList, prim.path))



if __name__ == "__main__":
    a = TestTop()
    a.test_UpdateCompositionAssetDependency()
