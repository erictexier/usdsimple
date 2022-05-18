
from collections import defaultdict
from xcore.xscene_schema import XSceneSchema as SCH_DEF
from meta_io.genericxml import GenericXml
 
class constant(object):
    """
    list of xmltag to map factory to
    """

    # for scenegraph
    attrlist = "arbitraryList"
    instance = "instance"
    scatter = "scatter"
    group = "group"
    scenetag = "scenegraphXML3D"
    lookfile = "lookFile"
    bounds = "bounds"
    xform = "xform"

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
    Property = SCH_DEF.layer_type_sublayer.Property
    def __init__(self):
        super(XLayerType, self).__init__(SCH_DEF.layer_type_sublayer.tag)

    def get_sublayers(self):
        return self.get_children()

##########################################################
# USD sublayer
class XPayload(XLayerType):
    Property = SCH_DEF.layer_type_payload.Property
    def __init__(self):
        super(XPayload, self).__init__(SCH_DEF.layer_type_payload.tag)


class XReference(XLayerType):
    Property = SCH_DEF.layer_type_reference.Property
    def __init__(self):
        super(XReference, self).__init__(SCH_DEF.layer_type_reference.tag)


class XSublayer(XLayerType):
    Property = SCH_DEF.layer_type_sublayer.Property
    def __init__(self):
        super(XSublayer, self).__init__(SCH_DEF.layer_type_sublayer.tag)


class XEmpty(XLayerType):
    Property = SCH_DEF.layer_type_empty.Property
    def __init__(self):
        super(XEmpty, self).__init__(SCH_DEF.layer_type_empty.tag)

##########################################################
# sublayer entry type
class XRootEntry(XSublayer):
    Property = SCH_DEF.entry_type.Property
    def __init__(self):
        super(XRootEntry, self).__init__(SCH_DEF.entry_type.tag)


class XAssetOpinion(XSublayer):
    Property = SCH_DEF.opinion_asset.Property
    def __init__(self):
        super(XAssetOpinion, self).__init__(SCH_DEF.opinion_asset.tag)

class XShotOpinion(XSublayer):
    Property = SCH_DEF.opinion_shot.Property
    def __init__(self):
        super(XShotOpinion, self).__init__(SCH_DEF.opinion_shot.tag)

### not finished
class XSeqLayer(XSublayer):
    Property = SCH_DEF.other_layer_type.Property
    def __init__(self):
        super(XSeqLayer, self).__init__(SCH_DEF.other_layer_type.tag)

class XLocLayer(XSublayer):
    Property = SCH_DEF.other_layer_type.Property
    def __init__(self):
        super(XLocLayer, self).__init__(SCH_DEF.other_layer_type.tag)

###########

class FromSptConfig(XScene):
    """Top level node for a bams queriable scenegraph (optional)"""
    Property = "RootDefinition"

    def __init__(self, tag=constant.scenetag):
        super(FromSptConfig, self).__init__(tag)
        self.__registered = defaultdict(list)
        # registe self as first one only
        if self.Property not in self.__registered:
            self.__registered[self.Property].append(self)

    def get_name(self):
        return ""



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
"""