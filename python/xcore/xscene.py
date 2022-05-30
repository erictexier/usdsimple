
import sys
from collections import defaultdict
from xcore.xscene_schema import XSceneSchema as SCH_DEF
from meta_io.genericxml import GenericXml
import json
PY3 = False
if sys.version_info.major == 3:
    from base64 import encodebytes as b64encode
    from base64 import decodebytes as b64decode
    PY3 = True
else:
    from base64 import encodestring as b64encode
    from base64 import decodestring as b64decode
 

class xconstant(object):
    """
    list of xmltag to map factory to
    """

    attribute = "attribute"
    encoded = "encoded"
    decoded = "decoded"
    fields = "%s%sfields" % (SCH_DEF.SDAT, SCH_DEF.SEP)
    variants = "%s%svariants" % (SCH_DEF.SDAT, SCH_DEF.SEP)

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
    Property = SCH_DEF.Layer_Type_layer.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Layer_Type_layer.tag if tag is None else tag
        super(XLayerType, self).__init__(tag)
        self.filetype = ""
        self._fields = dict()

    def set_fields(self, adict):
        self._fields.update(adict)

    def get_sublayers(self):
        return self.get_children()

##########################################################
class XStage(XScene):
    Property = SCH_DEF.Stage_Type.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Stage_Type.tag if tag is None else tag
        super(XStage, self).__init__(tag)
        self.filename = ""

class XStageAsset(XScene):
    Property = SCH_DEF.Stage_Type_asset.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Stage_Type_asset.tag if tag is None else tag
        super(XStageAsset, self).__init__(tag)

class XStageShot(XScene):
    Property = SCH_DEF.Stage_Type_shot.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Stage_Type_shot.tag if tag is None else tag
        super(XStageShot, self).__init__(tag)

class XStageSeq(XScene):
    Property = SCH_DEF.Stage_Type_seq.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Stage_Type_seq.tag if tag is None else tag
        super(XStageSeq, self).__init__(tag)

class XStageLoc(XScene):
    Property = SCH_DEF.Stage_Type_loc.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Stage_Type_loc.tag if tag is None else tag
        super(XStageLoc, self).__init__(tag)

##########################################################
# USD sublayer
class XPayload(XLayerType):
    Property = SCH_DEF.Layer_Type_payload.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Layer_Type_payload.tag if tag is None else tag
        super(XPayload, self).__init__(tag)

class XReference(XLayerType):
    Property = SCH_DEF.Layer_Type_reference.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Layer_Type_reference.tag if tag is None else tag
        super(XReference, self).__init__(tag)


class XSublayer(XLayerType):
    Property = SCH_DEF.Layer_Type_sublayer.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Layer_Type_sublayer.tag if tag is None else tag
        super(XSublayer, self).__init__(tag)


class XEmpty(XLayerType):
    Property = SCH_DEF.Layer_Type_empty.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Layer_Type_empty.tag if tag is None else tag
        super(XEmpty, self).__init__(tag)

##########################################################
# sublayer entry type
class XRootEntry(XSublayer):
    Property = SCH_DEF.Entry_Type.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Entry_Type.tag if tag is None else tag
        super(XRootEntry, self).__init__(tag)

class XRootEntryAsset(XRootEntry):
    Property = SCH_DEF.Entry_Type_asset.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Entry_Type_asset.tag if tag is None else tag
        super(XRootEntryAsset, self).__init__(tag)
        self.asset_type = None

    def set_asset_type(self, a_type_asset):
        self.asset_type = a_type_asset

class XRootEntryShot(XRootEntry):
    Property = SCH_DEF.Entry_Type_shot.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Entry_Type_shot.tag if tag is None else tag
        super(XRootEntryShot, self).__init__(tag)

class XRootEntrySequence(XRootEntry):
    Property = SCH_DEF.Entry_Type_seq.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Entry_Type_seq.tag if tag is None else tag
        super(XRootEntrySequence, self).__init__(tag)

class XRootEntryLocation(XRootEntry):
    Property = SCH_DEF.Entry_Type_loc.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Entry_Type_loc.tag if tag is None else tag
        super(XRootEntryLocation, self).__init__(tag)

# opinions
class XAssetOpinion(XSublayer):
    Property = SCH_DEF.Opinion_asset.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Opinion_asset.tag if tag is None else tag
        super(XAssetOpinion, self).__init__(tag)
        self.f_step = "[department]"

class XAssetOpinionDesc(XAssetOpinion):
    Property = SCH_DEF.Opinion_asset_desc.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Opinion_asset_desc.tag if tag is None else tag
        super(XAssetOpinionDesc, self).__init__(tag)


class XAssetOpinionGeom(XAssetOpinion):
    Property = SCH_DEF.Opinion_asset_geom.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Opinion_asset_geom.tag if tag is None else tag
        super(XAssetOpinionGeom, self).__init__(tag)


class XShotOpinion(XSublayer):
    Property = SCH_DEF.Opinion_shot.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Opinion_shot.tag if tag is None else tag
        super(XShotOpinion, self).__init__(tag)

class XShotOpinionManifest(XShotOpinion):
    Property = SCH_DEF.Opinion_shot_manifest.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Opinion_shot_manifest.tag if tag is None else tag
        super(XShotOpinionManifest, self).__init__(tag)

class XShotOpinionGeom(XShotOpinion):
    Property = SCH_DEF.Opinion_shot_geom.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Opinion_shot_geom.tag if tag is None else tag
        super(XShotOpinionGeom, self).__init__(tag)


### need more work later for seq and loc
class XLayerOther(XSublayer):
    Property = SCH_DEF.Layer_Type_layer_other.tag
    def __init__(self, tag=None):
        tag = SCH_DEF.Layer_Type_layer_other.tag if tag is None else tag
        super(XLayerOther, self).__init__(tag)


class InstanceAttrib(XScene):
    """Basic stupid Attribute class,  value are string with type named
    support only str, float and int for now
    """

    Property = "ATTRIBUTE"
    __maptype = {
        "int": "int",
        "str": "string",
        "unicode": "string",
        "float": "float",
        "bool": "bool",
    }

    def __init__(self, tag=xconstant.attribute):
        super(InstanceAttrib, self).__init__(tag)
        self.type = "string"
        self.value = ""
        self.name = ""

    def get_data():
        return self

    def before_to_xml(self):
        # this is a method that can be overwriten to check valid and format for xml
        pass


    def do_encode_value(self, value):
        # the test for this encoding and xml is not done TODO.
        
        if PY3:
            self.value = b64encode(bytes(json.dumps(value), "UTF-8")).decode('UTF-8')
        else:
            self.value = b64encode(json.dumps(value))

        self.type = xconstant.encoded
        return self.value

    def decode_value(self):
        if PY3:
            self.value = json.loads(b64decode(bytes(self.value, "UTF-8")).decode('UTF-8'))
        else:
            self.value = json.loads(b64decode(self.value))
        self.type = xconstant.decoded
        return self.value

    def set_data_with_type(self, args):
        try:
            name = args.pop("name")
            value = args.pop("value")
        except Exception as e:
            raise Exception("FOR NOW: {}".format(e))

        self.name = name
        if isinstance(value, dict):
            self.do_encode_value(value)
        else:

            self.type = self.__maptype[value.__class__.__name__]
            self.value = str(value)

class FieldsInstance(InstanceAttrib):
    Property = "fields"
    def __init__(self, tag=None):
        if tag is None:
            tag = xconstant.fields
        super(FieldsInstance, self).__init__(tag)
        self.__lookup = dict()
        self.key = ""
    
    def set_key(self, value):
        self.key = value

class VariantsInstance(InstanceAttrib):
    Property = "variants"
    def __init__(self, tag=None):
        if tag is None:
            tag = xconstant.variants
        super(VariantsInstance, self).__init__(tag)
        self.__lookup = dict()


# final gather
_XGenerator = {
    SCH_DEF.Layer_Type_layer.tag : XLayerType,
    SCH_DEF.Stage_Type.tag : XStage,
    SCH_DEF.Stage_Type_asset.tag : XStageAsset,
    SCH_DEF.Stage_Type_shot.tag : XStageShot,
    SCH_DEF.Stage_Type_seq.tag : XStageSeq,
    SCH_DEF.Stage_Type_loc.tag : XStageLoc,
    SCH_DEF.Layer_Type_payload.tag : XPayload,
    SCH_DEF.Layer_Type_reference.tag : XReference,
    SCH_DEF.Layer_Type_sublayer.tag : XSublayer,
    SCH_DEF.Layer_Type_empty.tag : XEmpty,
    SCH_DEF.Entry_Type.tag : XRootEntry,
    SCH_DEF.Entry_Type_asset.tag : XRootEntryAsset,
    SCH_DEF.Entry_Type_shot.tag : XRootEntryShot,
    SCH_DEF.Entry_Type_seq.tag : XRootEntrySequence,
    SCH_DEF.Entry_Type_loc.tag : XRootEntryLocation,
    SCH_DEF.Opinion_asset.tag : XAssetOpinion,
    SCH_DEF.Opinion_asset_desc.tag : XAssetOpinionDesc,
    SCH_DEF.Opinion_asset_geom.tag : XAssetOpinionGeom,
    SCH_DEF.Opinion_shot.tag : XShotOpinion,
    SCH_DEF.Opinion_shot_manifest.tag : XShotOpinionManifest,
    SCH_DEF.Opinion_shot_geom.tag : XShotOpinionGeom,
    SCH_DEF.Layer_Type_layer_other.tag : XLayerOther,

    xconstant.variants : VariantsInstance,
    xconstant.fields : FieldsInstance,
    xconstant.attribute: InstanceAttrib
}
