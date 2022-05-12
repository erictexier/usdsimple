from collections import namedtuple


class ConstantInfo(namedtuple('ConstantInfo', 'name type doc')):
    __slots__ = ()


# schema
class RootDefault(object):
    SDAT = 'sda'

    # the name here is what can be found at config level
    payload_desc = ConstantInfo("payload_str", "payload", "what we use as payload key")
    reference_desc = ConstantInfo("reference_str", "reference", "what we use as reference key")
    sublayer_desc = ConstantInfo("sublayer_str", "sublayer", "what we use as sublayer key")

    # basic type
    basic_type_char = ConstantInfo("usd_char", "character", "what we use as sublayer key")
    basic_type_elm = ConstantInfo("usd_elem", "element", "what we use as sublayer key")
    basic_type_shot = ConstantInfo("usd_shot", "shot", "Not Done")
    basic_type_seq = ConstantInfo("usd_seq", "sequence", "Not Done")

    basic_types = [basic_type_char, basic_type_elm, basic_type_shot, basic_type_seq]

    # layer type
    # opinion
    opinion_desc = ConstantInfo('sdal_opinion_geom', 'description', 'the model variant identificator')
    opinion_geom = ConstantInfo('sdal_opinion_desc', 'geometry', 'the geom identificator')
    layer_type_opinion = ConstantInfo('sdal_opinion_type', 'opinion', 'the type option')

    layer_type_payload = ConstantInfo("sdal_payload", "payload", "refer a payload type layer")
    layer_type_reference = ConstantInfo("sdal_reference", "reference", "refer a reference type layer")
    layer_type_sublayer = ConstantInfo("sdal_sublayer", "sublayer", "refer a sublayer type layer")

    layer_types = [layer_type_payload, layer_type_reference, layer_type_sublayer, layer_type_opinion]

SCH_DEF =  RootDefault

class Modelvariant(namedtuple('modelvariant', 'name step model_variant_name')):
    __slots__ = ()

# definition class hierachy
# base
class Xroot(object):
    VALID_LAYER_TYPE = set()
    def __init__(self, atype):
        self._type = "%s%s" % (SCH_DEF.SDAT, atype)

class XLayerType(Xroot):
    def __init__(self, name, layertype):
        super(XLayerType, self).__init__(layertype)
        self.name = name
        self.downstream = list()
        self.parent = None

    def add_downstream(self, child):
        self.downstream.append(child)
        if isinstance(child, XLayerType):
            self.downstream.append(child)
            child.parent = self

    def add_downstreams(self, children):
        self.downstream.append(child)
        for child in children:
            if isinstance(child, XLayerType):
                self.downstream.append(child)
                child.parent = self

class XrootEntry(XLayerType):
    def __init__(self, name, atype):
        super(XrootEntry, self).__init__(name, atype)

    def get_sublayers(self):
        return self.downstream

    def __repr__(self):
        return "type %s, name %s, downstream %s" % (self._type, self.name, [x.name for x in self.downstream])


# opinions
class XassetOpinion(XLayerType):
    def __init__(self, name, step, model_variant_name):
        self.step = step
        self.model_variant_name = model_variant_name
        self.description = XLayerType(SCH_DEF.opinion_desc.name, SCH_DEF.opinion_desc.type)
        self.geom = XLayerType(SCH_DEF.opinion_geom.name, SCH_DEF.opinion_geom.type)
        super(XassetOpinion, self).__init__(name, SCH_DEF.layer_type_opinion.type, [self.description, self.geom])

class XshotOpinion(XLayerType):
    def __init__(self, name, step):
        self.step = step
        self.description = XLayerType(SCH_DEF.opinion_desc.name, SCH_DEF.opinion_desc.type)
        self.geom = XLayerType(SCH_DEF.asset_opinion_geom.name, SCH_DEF.asset_opinion_geom.type)
        super(XshotOpinion, self).__init__(name, SCH_DEF.layer_type_opinion.type, [self.description, self.geom])

# basic type
class XassetElement(XLayerType):
    SHOW_OPINIONS = []
    def __init__(self, name):
        list_of_downstream = []
        for x in self.SHOW_OPINIONS:
            list_of_downstream.append(
                XassetOpinion(x.name, x.step, x.model_variant_name)
            )
        super(XassetElement, self).__init__(name, SCH_DEF.basic_type_elm.type, list_of_downstream)

class XassetChar(XLayerType):
    SHOW_OPINIONS = []
    def __init__(self, name):
        list_of_downstream = []
        for x in self.SHOW_OPINIONS:
            print("x"*30, x)
            list_of_downstream.append(
                XassetOpinion(x.name, x.step, x.model_variant_name)
            )
        super(XassetChar, self).__init__(name, SCH_DEF.basic_type_char.type, list_of_downstream)


class Xshot(XrootEntry):
    SHOW_OPINIONS = []
    def __init__(self, name):
        list_of_downstream = []
        for x in self.SHOW_OPINIONS:
            list_of_downstream.append(
                XshotOpinion(x.name, x.step)
            )
        super(Xshot, self).__init__(name, SCH_DEF.basic_type_shot.type, list_of_downstream)


class Xscene(object):
    Property = "Xscene"
    PrefixNaming = "X"
    __filter = set()
    def __init__(self, tag=None):
        super(Xscene, self).__init__()
        print("init xscene root %s" % tag)
        self.tag = tag

    @classmethod
    def set_filter(cls, property_list):
        cls.__filter = set(property_list)

    @classmethod
    def context_factory(cls, 
                        default_classes,
                        base_class=None,
                        upmethod = None,
                        log=None):
        """Generic class creation 
        Args:
            default_classes
        
        
        """

        result = dict()
        if base_class == None:
            base_class = Xscene

        class XsceneDefault(base_class):
            log = None
            __doc__ = ("py representation XSceneDefault",)

        if upmethod is None:
            upmethod = dict()

        class_def = list()
        for class_base in default_classes:
            upmethod.update(
                {
                    "log": log,
                    "Property": class_base,
                    "__doc__": "py representation %s" % class_base,
                }
            )
            class_def.append(type(cls.PrefixNaming + class_base, (base_class,), upmethod,))

        cls.__filter.update(default_classes)
        named = [x.Property for x in class_def]
        result = dict(zip(named, class_def))
        # has a default
        result.update({"default": XsceneDefault})
        return result

def __init__(self, name, extra=10):
    print(name, extra)

if __name__ == '__main__':
    assetname = 'callan'
    # print(XassetChar(assetname))
    # print(XassetElement(assetname))
    # shotname = "xseq_001"
    # print(Xshot(shotname))

    result = Xscene.context_factory(
                            ["Xopinion"],
                            base_class=XassetChar,
                            upmethod = {"SHOW_OPINIONS": [Modelvariant(assetname, "modeling", "original"),
                                                          Modelvariant(assetname, "surfacing", "original")],
                            "__init__" : __init__
                                                          },
                            log=None)
    print(result)
    a = result['Xopinion'](assetname)
    print(a.SHOW_OPINIONS)
    #print(a)