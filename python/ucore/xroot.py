from collections import namedtuple


class ConstantInfo(namedtuple('ConstantInfo', 'name type doc')):
    __slots__ = ()


# schema
class RootDefinition(object):
    SDAT = 'sda'
    SEP = '::'

    # basic type
    basic_type_asset = ConstantInfo('%s%sasset' % (SDAT, SEP), 'asset', 'can be instanced from a shot')
    basic_type_shot = ConstantInfo('%s%sshot' % (SDAT, SEP), 'shot', 'collection of asset instance')
    basic_type_seq = ConstantInfo('%s%sseq' % (SDAT, SEP), 'sequence', 'collection of shot')

    basic_types = [basic_type_asset, basic_type_shot, basic_type_seq]

    # usd layer type
    layer_type_payload = ConstantInfo('%s%spayload' % (SDAT, SEP), 'payload', 'refer a payload type layer')
    layer_type_reference = ConstantInfo('%s%sreference' % (SDAT, SEP), 'reference', 'refer a reference type layer')
    layer_type_sublayer = ConstantInfo('%s%ssublayer' % (SDAT, SEP), 'sublayer', 'refer a sublayer type layer')

    # opinion for model
    layer_type_opinion = ConstantInfo('%s%sopinion_type' % (SDAT, SEP), 'opinion', 'the type option')
    opinion_desc = ConstantInfo('%s%sopinion_geom' % (SDAT, SEP), 'description', 'model variant identificator')
    opinion_geom = ConstantInfo('%s%sopinion_desc' % (SDAT, SEP), 'geometry', 'the geom identificator')


    layer_types = [layer_type_payload, layer_type_reference, layer_type_sublayer, layer_type_opinion]

SCH_DEF =  RootDefinition

class Modelvariant(namedtuple('modelvariant', 'name step model_variant_name')):
    __slots__ = ()

# definition class hierachy
# base
class Xroot(object):
    VALID_LAYER_TYPE = set()
    def __init__(self, atype):
        self._type = '%s%s' % (SCH_DEF.SDAT, atype)

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
        return 'type %s, name %s, downstream %s' % (self._type, self.name, [x.name for x in self.downstream])


# opinions
class XassetOpinion(XLayerType):
    def __init__(self, name, step, model_variant_name):
        self.step = step
        self.model_variant_name = model_variant_name
        self.description = XLayerType(SCH_DEF.opinion_desc.name, SCH_DEF.opinion_desc.type)
        self.geom = XLayerType(SCH_DEF.opinion_geom.name, SCH_DEF.opinion_geom.type)
        super(XassetOpinion, self).__init__(name, SCH_DEF.layer_type_opinion.type)
        self.add_downstreams([self.description, self.geom])


class XShotLayers(XLayerType):
    def __init__(self, name, step):
        self.step = step
        self.description = XLayerType(SCH_DEF.opinion_desc.name, SCH_DEF.opinion_desc.type)
        self.geom = XLayerType(SCH_DEF.opinion_geom.name, SCH_DEF.opinion_geom.type)
        super(XShotLayers, self).__init__(name, SCH_DEF.layer_type_opinion.type)
        

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
            print('x'*30, x)
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
                XShotLayers(x.name, x.step)
            )
        super(Xshot, self).__init__(name, SCH_DEF.basic_type_shot.type, list_of_downstream)


class Xscene(object):
    Property = 'Xscene'
    PrefixNaming = 'X'
    __filter = set()
    def __init__(self, tag=None):
        super(Xscene, self).__init__()
        print('init xscene root %s' % tag)
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