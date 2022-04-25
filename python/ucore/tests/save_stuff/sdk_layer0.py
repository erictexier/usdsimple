import os, platform, itertools, sys, unittest
preferredResolver = os.environ.get(
    "TEST_SDF_LAYER_RESOLVER", "Sdf_TestResolver")

from pxr import Ar
Ar.SetPreferredResolver(preferredResolver)

from pxr import Sdf, Tf, Ar, Plug

class top(unittest.TestCase):
    # def assertEqual(self, a, b):
    #     print("\nTest %s" % (a==b))
    #     # print(a,b)
    #     pass

    def test_IdentifierWithArgs(self):
        # note: SDF_FORMAT_ARGS
        paths = [
            ("foo.sdf", 
             "foo.sdf", 
             {}),

            ("foo.sdf1!@#$%^*()-_=+[{]}|;:',<.>", 
             "foo.sdf1!@#$%^*()-_=+[{]}|;:',<.>", 
             {}),

            ("foo.sdf:SDF_FORMAT_ARGS:a=b&c=d", 
             "foo.sdf",
             {"a":"b", "c":"d"}),

            ("foo.sdf?otherargs&evenmoreargs:SDF_FORMAT_ARGS:a=b&c=d", 
             "foo.sdf?otherargs&evenmoreargs",
             {"a":"b", "c":"d"}),
        ]
        
        for (identifier, path, args) in paths:
            splitPath, splitArgs = Sdf.Layer.SplitIdentifier(identifier)
            # print("------>", identifier,splitPath, splitArgs)
            self.assertEqual(path, splitPath)
            self.assertEqual(args, splitArgs)

            joinedIdentifier = Sdf.Layer.CreateIdentifier(splitPath, splitArgs)
            self.assertEqual(identifier, joinedIdentifier)

    def test_SetIdentifier(self):
        layer = Sdf.Layer.CreateAnonymous()

        # Can't change a layer's identifier if another layer with the same
        # identifier and resolved path exists.
        existingLayer = Sdf.Layer.CreateNew("testSetIdentifier.sdf")
        with self.assertRaises(Tf.ErrorException):
            print(layer.identifier , existingLayer.identifier)
            layer.identifier = existingLayer.identifier


        # Can't change a layer's identifier to the empty string.
        with self.assertRaises(Tf.ErrorException):
            layer.identifier = ""

        # Can't change a layer's identifier to an anonymous layer identifier.
        with self.assertRaises(Tf.ErrorException):
            layer.identifier = "anon:testing"

    def test_SetIdentifierWithArgs(self):
        layer = Sdf.Layer.CreateAnonymous()
        layer.Export("testSetIdentifierWithArgs.sdf")

        layer = Sdf.Layer.FindOrOpen(
            "testSetIdentifierWithArgs.sdf", args={"a":"b"})
        self.assertTrue(layer)
        print(layer.identifier) 

        # Can't change arguments when setting a new identifier
        with self.assertRaises(Tf.ErrorException):
            layer.identifier = Sdf.Layer.CreateIdentifier(
                "testSetIdentifierWithArgs.sdf", {"a":"c"})

        with self.assertRaises(Tf.ErrorException):
            layer.identifier = Sdf.Layer.CreateIdentifier(
                "testSetIdentifierWithArgs.sdf", {"b":"d"})

        # Can change the identifier if we leave the args the same.
        layer.identifier = Sdf.Layer.CreateIdentifier(
            "testSetIdentifierWithArgsNew.sdf", {"a":"b"})
        splitPath, splitArgs = Sdf.Layer.SplitIdentifier(layer.identifier)
        self.assertEqual(splitPath, "testSetIdentifierWithArgs.sdf")
        self.assertEqual(splitArgs, {"a":"b"})

    def test_OpenWithInvalidFormat(self):
        l = Sdf.Layer.FindOrOpen('foo.invalid')
        self.assertIsNone(l)

        # XXX: 
        # OpenAsAnonymous raises a coding error when it cannot determine a
        # file format. This is inconsistent with FindOrOpen and is purely
        # historical.
        with self.assertRaises(Tf.ErrorException):
            l = Sdf.Layer.OpenAsAnonymous('foo.invalid')

    def test_FindWithAnonymousIdentifier(self):
        def _TestWithTag(tag):
            layer = Sdf.Layer.CreateAnonymous(tag)
            layerId = layer.identifier
            self.assertEqual(Sdf.Layer.Find(layerId), layer)
            del layer
            self.assertNotIn(
                layerId, [l.identifier for l in Sdf.Layer.GetLoadedLayers()])
            self.assertFalse(Sdf.Layer.Find(layerId))

        _TestWithTag("")
        _TestWithTag(".sdf")
        _TestWithTag(".invalid")
        _TestWithTag("test")
        _TestWithTag("test.invalid")
        _TestWithTag("test.sdf")

    def test_AnonymousIdentifiersDisplayName(self):
        # Ensure anonymous identifiers work as expected

        ident = 'anonIdent.sdf'
        l = Sdf.Layer.CreateAnonymous(ident)
        self.assertEqual(l.GetDisplayName(), ident)

        identWithColons = 'anonIdent:afterColon.sdf'
        l = Sdf.Layer.CreateAnonymous(identWithColons)
        self.assertEqual(l.GetDisplayName(), identWithColons)

        l = Sdf.Layer.CreateAnonymous()
        self.assertEqual(l.GetDisplayName(), '')
    @unittest.skipIf(platform.system() == "Windows" and
                     not hasattr(Ar.Resolver, "CreateIdentifier"),
                     "This test case currently fails on Windows due to "
                     "path canonicalization issues except with Ar 2.0.")
    def test_UpdateAssetInfo(self):
        # Test that calling UpdateAssetInfo on a layer whose resolved
        # path hasn't changed doesn't cause notification to be sent.
        layer = Sdf.Layer.CreateNew('TestUpdateAssetInfo.sdf')
        self.assertTrue(layer)

        class _Listener:
            def __init__(self):
                self._listener = Tf.Notice.RegisterGlobally(
                    Sdf.Notice.LayersDidChange, self._HandleNotice)
                self.receivedNotice = False

            def _HandleNotice(self, notice, sender):
                self.receivedNotice = True
                print(11)

        listener = _Listener()

        oldResolvedPath = layer.resolvedPath
        print(1)
        layer.UpdateAssetInfo()
        print(2)
        newResolvedPath = layer.resolvedPath

        self.assertEqual(oldResolvedPath, newResolvedPath)
        self.assertFalse(listener.receivedNotice)


if __name__ == "__main__":
    a = top()
    # a.test_IdentifierWithArgs()
    # a.test_SetIdentifier()
    # a.test_SetIdentifierWithArgs()
    # a.test_OpenWithInvalidFormat()
    # a.test_FindWithAnonymousIdentifier()
    # a.test_AnonymousIdentifiersDisplayName()

    a.test_UpdateAssetInfo()
