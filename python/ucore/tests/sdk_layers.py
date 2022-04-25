

import os, platform, itertools, sys, unittest
# preferredResolver = os.environ.get(
#     "TEST_SDF_LAYER_RESOLVER", "Sdf_TestResolver")
# from pxr import Ar
# Ar.SetPreferredResolver(preferredResolver)

from pxr import Sdf, Tf, Plug, Usd

def _EmptyLayer():
    stage = Usd.Stage.CreateInMemory()
    # return 
    # stage.GetRootLayer().ExportToString()
    return stage.GetRootLayer()

class top(unittest.TestCase):
    # def assertEqual(self, a, b):
    #     print("\nTest %s" % (a==b))
    #     # print(a,b)
    #     pass

    def test_UpdateCompositionAssetDependency(self):
        assetStage = None
        if 1:
            
            emptyL = Sdf.Layer.CreateNew("sublayer_1.usda", args={"format": "usda"})
            assetPrim = UsdGeom.Xform.Define(assetStage, "/%s" % dest.primname).GetPrim()
            assetStage.SetDefaultPrim(assetPrim)
            Usd.Stage.Open(emptyL).GetRootLayer().Save()

            emptyL = Sdf.Layer.CreateNew("sublayer_2.usda", args={"format": "usda"})
            Usd.Stage.Open(emptyL).GetRootLayer().Save()

            emptyL = Sdf.Layer.CreateNew("ref_1.usda", args={"format": "usda"})
            Usd.Stage.Open(emptyL).GetRootLayer().Save()

            emptyL = Sdf.Layer.CreateNew("ref_2.usda", args={"format": "usda"})
            Usd.Stage.Open(emptyL).GetRootLayer().Save()

            emptyL = Sdf.Layer.CreateNew("payload_1.usda", args={"format": "usda"})
            Usd.Stage.Open(emptyL).GetRootLayer().Save()

            emptyL = Sdf.Layer.CreateNew("payload_2.usda", args={"format": "usda"})
            Usd.Stage.Open(emptyL).GetRootLayer().Save()

            srcLayer = Sdf.Layer.CreateNew("testLayersave.usda", args={"format": "usda"})
            assetStage = Usd.Stage.Open(srcLayer)
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
    payload = @payload_1.usda@</Payload>
    references = [
        @ref_1.usda@</Ref>,
        @ref_2.usda@</Ref2>
    ]
)
{
    def "Child" (
        payload = @payload_1.usda@</Payload>
        references = [
            @ref_1.usda@</Ref>,
            @ref_2.usda@</Ref2>
        ]
    )
    {
    }

    variantSet "v" = {
        "x" (
            payload = [
                @payload_1.usda@</Payload>, 
                @payload_2.usda@</Payload2>
            ]
            references = [
                @ref_1.usda@</Ref>,
                @ref_2.usda@</Ref2>
            ]
        ) {
            def "ChildInVariant" (
                payload = [
                    @payload_1.usda@</Payload>, 
                    @payload_2.usda@</Payload2>
                ]
                references = [
                    @ref_1.usda@</Ref>,
                    @ref_2.usda@</Ref2>
                ]
            )
            {
            }
        }
    }
}
        '''

        srcLayer.ImportFromString(srcLayerStr)
        return
        # Calling UpdateCompositionAssetDependency with an empty old layer path
        # is not allowed.
        origLayer = srcLayer.ExportToString()
        # srcLayer.Export("testLayersave.sdf")
        # if assetStage:
        #     assetStage.GetRootLayer().Save()
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
    a = top()
    a.test_UpdateCompositionAssetDependency()
