
from collections import defaultdict
from xcore.xscene_schema import XSceneSchema as SCH_DEF
from meta_io.genericxml import GenericXml
 
class xconstant(object):
    """
    list of xmltag to map factory to
    """
    pass

########################################################
# definition class hierachy
# base
class XScene(GenericXml):
    Property = "XScene"
    __filter = set()
    _sep = "/"

    def __init__(self, tag=None):
        super(XScene, self).__init__(tag)

    @classmethod
    def set_filter(cls, property_list):
        cls.__filter = set(property_list)

    def print_nice(self, max_char=120, tab=""):
        """overwrite base class
        Args:
            max_char(int): clip the value of attrib
            tab(string): indent
        """

        if self.Property in self.__filter:
            super(XScene, self).print_nice(max_char, tab)
        else:
            for ch in self.get_children():
                ch.print_nice(max_char=max_char, tab=tab + " " * 4)

    def get_name(self):
        if hasattr(self, "name"):
            return self.name
        return self.Property

    def set_geom_instance_data(self, geom):
        # some custom runtime data
        # not serialysed
        self._geom = geom

    def get_geom_instance_data(self):
        # not serialized
        if hasattr(self, "_geom"):
            return self._geom
        return None

    def get_path(self):
        """

        Returns:
             path from the root
        """

        parent = self.get_parent()
        if parent is None:
            return self.get_name()
        pp = parent.get_path()
        if pp != "":
            return pp + self._sep + self.get_name()
        else:
            return self.get_name()

    def delegate(self, args):
        """build a dict with _x args"""
        d = dict()
        for x in args:
            d.update({"_@x%s" % x: args.get(x, "")})
        self.__dict__.update(d)

    def get_delegate(self):
        """build a dict with _x args"""
        d = dict()
        for x in self.__dict__:
            if x.startswith("_@x"):
                d.update({x[3:]: self.__dict__[x]})
        return d

    @classmethod
    def factory(cls, default_classes, log=None, mother_class=None):
        class SceneDefault(XScene):
            log = None
            __doc__ = ("py representation SceneDefault",)

        if mother_class == None:
            mother_class = XScene
        upmethod = dict()
        class_def = list()
        for classRoot in default_classes:
            upmethod.update(
                {
                    "log": log,
                    "Property": classRoot,
                    "__doc__": "py representation %s" % classRoot,
                }
            )
            class_def.append(
                type(
                    classRoot + "Xml",
                    (mother_class,),
                    upmethod,
                )
            )
        cls.__filter.update(default_classes)
        named = [x.Property for x in class_def]
        result = dict(zip(named, class_def))
        result.update({"default": SceneDefault})
        return result

class XLayerType(XScene):
    Property = SCH_DEF.Layer_Type_sublayer.Property
    def __init__(self):
        super(XLayerType, self).__init__(SCH_DEF.Layer_Type_sublayer.tag)
        self._filetype = ""
        self._fields = dict()

    def get_sublayers(self):
        return self.get_children()

##########################################################
class XStage(XScene):
    Property = SCH_DEF.Stage_Type.Property
    def __init__(self):
        super(XStage, self).__init__(SCH_DEF.Stage_Type.tag)
        self.filename = ""

class XStageAsset(XScene):
    Property = SCH_DEF.Stage_Type_asset.Property
    def __init__(self):
        super(XStageAsset, self).__init__(SCH_DEF.Stage_Type_asset.tag)

class XStageShot(XScene):
    Property = SCH_DEF.Stage_Type_shot.Property
    def __init__(self):
        super(XStageShot, self).__init__(SCH_DEF.Stage_Type_shot.tag)

class XStageSeq(XScene):
    Property = SCH_DEF.Stage_Type_seq.Property
    def __init__(self):
        super(XStageSeq, self).__init__(SCH_DEF.Stage_Type_seq.tag)

class XStageLoc(XScene):
    Property = SCH_DEF.Stage_Type_loc.Property
    def __init__(self):
        super(XStageLoc, self).__init__(SCH_DEF.Stage_Type_loc.tag)

##########################################################
# USD sublayer
class XPayload(XLayerType):
    Property = SCH_DEF.Layer_Type_payload.Property
    def __init__(self):
        super(XPayload, self).__init__(SCH_DEF.Layer_Type_payload.tag)


class XReference(XLayerType):
    Property = SCH_DEF.Layer_Type_reference.Property
    def __init__(self):
        super(XReference, self).__init__(SCH_DEF.Layer_Type_reference.tag)


class XSublayer(XLayerType):
    Property = SCH_DEF.Layer_Type_sublayer.Property
    def __init__(self):
        super(XSublayer, self).__init__(SCH_DEF.Layer_Type_sublayer.tag)


class XEmpty(XLayerType):
    Property = SCH_DEF.Layer_Type_empty.Property
    def __init__(self):
        super(XEmpty, self).__init__(SCH_DEF.Layer_Type_empty.tag)

##########################################################
# sublayer entry type
class XRootEntry(XSublayer):
    Property = SCH_DEF.Entry_Type.Property
    def __init__(self):
        super(XRootEntry, self).__init__(SCH_DEF.Entry_Type.tag)

class XRootEntryAsset(XRootEntry):
    Property = SCH_DEF.Entry_Type_asset.Property
    def __init__(self):
        super(XRootEntryAsset, self).__init__(SCH_DEF.Entry_Type_asset.tag)
        self.asset_type = None

class XRootEntryShot(XRootEntry):
    Property = SCH_DEF.Entry_Type_shot.Property
    def __init__(self):
        super(XRootEntryShot, self).__init__(SCH_DEF.Entry_Type_shot.tag)

class XRootEntrySequence(XRootEntry):
    Property = SCH_DEF.Entry_Type_seq.Property
    def __init__(self):
        super(XRootEntrySequence, self).__init__(SCH_DEF.Entry_Type_seq.tag)

class XRootEntryLocation(XRootEntry):
    Property = SCH_DEF.Entry_Type_loc.Property
    def __init__(self):
        super(XRootEntryLocation, self).__init__(SCH_DEF.Entry_Type_loc.tag)

# opinions
class XAssetOpinion(XSublayer):
    Property = SCH_DEF.opinion_asset.Property
    def __init__(self):
        super(XAssetOpinion, self).__init__(SCH_DEF.opinion_asset.tag)

class XAssetOpinionDesc(XAssetOpinion):
    Property = SCH_DEF.opinion_asset_desc.Property
    def __init__(self):
        super(XAssetOpinionDesc, self).__init__(SCH_DEF.opinion_asset_desc.tag)

class XAssetOpinionGeom(XAssetOpinion):
    Property = SCH_DEF.opinion_asset_geom.Property
    def __init__(self):
        super(XAssetOpinionGeom, self).__init__(SCH_DEF.opinion_asset_geom.tag)


class XShotOpinion(XSublayer):
    Property = SCH_DEF.opinion_shot.Property
    def __init__(self):
        super(XShotOpinion, self).__init__(SCH_DEF.opinion_shot.tag)

class XShotOpinionManifest(XShotOpinion):
    Property = SCH_DEF.opinion_shot_manifest.Property
    def __init__(self):
        super(XShotOpinionManifest, self).__init__(SCH_DEF.opinion_shot_manifest.tag)

class XShotOpinionGeom(XShotOpinion):
    Property = SCH_DEF.opinion_shot_geom.Property
    def __init__(self):
        super(XShotOpinionGeom, self).__init__(SCH_DEF.opinion_shot_geom.tag)


### need more work later for seq and loc
class XLayerOther(XSublayer):
    Property = SCH_DEF.Layer_Type_layer_other.Property
    def __init__(self):
        super(XLayerOther, self).__init__(SCH_DEF.Layer_Type_layer_other.tag)

# final gather
_XGen = {
    XStage.Property: XStage,
    XStageAsset.Property: XStageAsset,
    XStageShot.Property: XStageShot,
    XStageSeq.Property: XStageSeq,
    XStageLoc.Property: XStageLoc,
    XLayerType.Property : XLayerType,
    XPayload.Property : XPayload,
    XReference.Property : XReference,
    XSublayer.Property: XSublayer,
    XEmpty.Property: XEmpty,
    XRootEntry.Property: XRootEntry,
    XRootEntryAsset.Property: XRootEntryAsset,
    XRootEntryShot.Property:XRootEntryShot,
    XRootEntrySequence.Property:XRootEntrySequence,
    XRootEntryLocation.Property:XRootEntryLocation,
    XAssetOpinion.Property:XAssetOpinion,
    XAssetOpinionDesc.Property: XAssetOpinionDesc,
    XAssetOpinionGeom.Property: XAssetOpinionGeom,
    XShotOpinion.Property: XShotOpinion,
    XShotOpinionManifest.Property: XShotOpinionManifest,
    XShotOpinionGeom.Property: XShotOpinionGeom,
    XLayerOther.Property: XLayerOther
}
###########
'''
class FromSptConfig(XScene):
    """Top level node for a queriable scenegraph (optional)"""
    Property = "RootDefinition"

    def __init__(self, tag=constant.scenetag):
        super(FromSptConfig, self).__init__(tag)
        self.__registered = defaultdict(list)
        # registe self as first one only
        if self.Property not in self.__registered:
            self.__registered[self.Property].append(self)

    def get_name(self):
        return ""

    def build_from_conf(self, conf):

_Generator = {
    "ymlconfig": FromSptConfig,
}
"""
_Generator = {
    "scenegraph": XRootEntry,
    "scenegraphXML3D": ScenegraphXml,
    "group": GroupXScene,
    "reference": InstanceXScene,
    "abc": InstanceXScene,
    constant.instanceanim: InstanceAnimXScene,
    constant.instancecrowds: InstanceCrowdsXScene,
    constant.instancecamera: InstanceCameraXScene,
    constant.instancescatter: InstanceScatterXScene,
    constant.instanceasset: InstanceSAsset,
    constant.instancemtl: InstanceMtlXml,
}
_Generator.update(InstanceXScene.get_factory())
'''