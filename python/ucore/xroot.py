from collections import namedtuple


class ConstantInfo(namedtuple("ConstantInfo", "tag type doc")):
    __slots__ = ()


# schema
class RootDefinition(object):
    SDAT = "sda"
    SEP = "::"

    # usd layer type
    layer_type_payload = ConstantInfo(
        "%s%spayload" % (SDAT, SEP), "payload", "refer a payload type layer"
    )
    layer_type_reference = ConstantInfo(
        "%s%sreference" % (SDAT, SEP), "reference", "refer a reference type layer"
    )
    layer_type_sublayer = ConstantInfo(
        "%s%ssublayer" % (SDAT, SEP), "sublayer", "refer a sublayer type layer"
    )
    layer_type_empty = ConstantInfo(
        "%s%sempty" % (SDAT, SEP), "empty", "refer to an empty layer"
    )

    usd_layer_types = [
        layer_type_payload,
        layer_type_reference,
        layer_type_sublayer,
        layer_type_empty,
    ]

    # basic new type
    basic_type_asset = ConstantInfo(
        "%s%sasset" % (SDAT, SEP), "asset", "can be instanced from a shot"
    )
    basic_type_shot = ConstantInfo(
        "%s%sshot" % (SDAT, SEP), "shot", "collection of asset instance"
    )
    basic_type_seq = ConstantInfo(
        "%s%sseq" % (SDAT, SEP), "sequence", "collection of shot"
    )

    basic_types = [basic_type_asset, basic_type_shot, basic_type_seq]

    # entry
    entry_type = ConstantInfo(
        "%s%sentry" % (SDAT, SEP), "entry", "list of option with or without usd prim"
    )

    # opinion for asset
    opinion_asset = ConstantInfo(
        "%s%sopinion_asset" % (SDAT, SEP), "opinionasset", "type opinion for asset"
    )
    opinion_asset_desc = ConstantInfo(
        "%s%sopinion_asset_desc" % (SDAT, SEP),
        "descriptionasset",
        "model variant identificator",
    )
    opinion_asset_geom = ConstantInfo(
        "%s%sopinion_asset_geom" % (SDAT, SEP),
        "geometryasset",
        "the geom identificator",
    )

    # opinion for shot
    opinion_shot = ConstantInfo(
        "%s%sopinion_shot" % (SDAT, SEP), "opinionshot", "type opinion for shot"
    )
    opinion_shot_manifest = ConstantInfo(
        "%s%sopinion_shot_manifest" % (SDAT, SEP),
        "descriptionshot",
        "model variant identificator",
    )
    opinion_shot_geom = ConstantInfo(
        "%s%sopinion_shot_geom" % (SDAT, SEP), "geometryshot", "the geom identificator"
    )

    # sublayer
    other_layer_type = ConstantInfo(
        "%s%ssublayer_type" % (SDAT, SEP), "sublayer", "other"
    )

    sda_type = [
        entry_type,
        opinion_asset,
        opinion_asset_desc,
        opinion_asset_geom,
        opinion_shot,
        opinion_shot_manifest,
        opinion_shot_geom,
        other_layer_type,
    ]

    _all__ = usd_layer_types + basic_types + sda_type


SCH_DEF = RootDefinition

########################################################
# definition class hierachy
# base
class XRoot(object):
    def __init__(self, tag):
        self._tag = tag


class XLayerType(XRoot):
    def __init__(self, tag):
        super(XLayerType, self).__init__(tag)
        self.downstream = list()
        self.parent = None

    def add_downstreams(self, children):
        for child in children:
            if isinstance(child, XLayerType):
                self.downstream.append(child)
                child.parent = self

    def get_sublayers(self):
        return self.downstream

    def __repr__(self):
        return "type %s, tag %s, downstream %s" % (
            self._type,
            self.tag,
            [x.tag for x in self.downstream],
        )


class XPayload(XLayerType):
    def __init__(self):
        super(XPayload, self).__init__(SCH_DEF.layer_type_payload.tag)


class XReference(XLayerType):
    def __init__(self):
        super(XReference, self).__init__(SCH_DEF.layer_type_reference.tag)


class XSublayer(XLayerType):
    def __init__(self):
        super(XSublayer, self).__init__(SCH_DEF.layer_type_sublayer.tag)


class XEmpty(XLayerType):
    def __init__(self):
        super(XEmpty, self).__init__(SCH_DEF.layer_type_empty.tag)


class XRootEntry(XSublayer):
    def __init__(self):
        super(XRootEntry, self).__init__(SCH_DEF.entry_type.tag)




##########################################################
# sublayer entry type


class XShotlayer(XLayerType):
    def __init__(self, tag, step):
        self.step = step
        self.geom = XLayerType(SCH_DEF.opinion_geom.tag, SCH_DEF.opinion_geom.type)
        super(XShotlayer, self).__init__(tag, SCH_DEF.layer_type_opinion.type)


class XassetOpinion(XLayerType):
    def __init__(self, tag, step, model_variant_name):
        self.step = step
        self.model_variant_name = model_variant_name
        self.description = XLayerType(
            SCH_DEF.opinion_desc.tag, SCH_DEF.opinion_desc.type
        )
        self.geom = XLayerType(SCH_DEF.opinion_geom.tag, SCH_DEF.opinion_geom.type)
        super(XassetOpinion, self).__init__(tag, SCH_DEF.layer_type_opinion.type)
        self.add_downstreams([self.description, self.geom])


# basic type
class XassetElement(XLayerType):
    SHOW_OPINIONS = []

    def __init__(self, tag):
        list_of_downstream = []
        for x in self.SHOW_OPINIONS:
            list_of_downstream.append(XassetOpinion(x.tag, x.step, x.model_variant_tag))
        super(XassetElement, self).__init__(
            tag, SCH_DEF.basic_type_elm.type, list_of_downstream
        )


class XassetChar(XLayerType):
    SHOW_OPINIONS = []

    def __init__(self, tag):
        list_of_downstream = []
        for x in self.SHOW_OPINIONS:
            list_of_downstream.append(
                XassetOpinion(x.tag, x.step, x.model_variant_name)
            )
        super(XassetChar, self).__init__(
            tag, SCH_DEF.basic_type_char.type, list_of_downstream
        )


class Xshot(XRootEntry):
    SHOW_OPINIONS = []

    def __init__(self, tag):
        list_of_downstream = []
        for x in self.SHOW_OPINIONS:
            list_of_downstream.append(XShotLayers(x.tag, x.step))
        super(Xshot, self).__init__(
            tag, SCH_DEF.basic_type_shot.type, list_of_downstream
        )


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
    def context_factory(cls, default_classes, base_class=None, upmethod=None, log=None):
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
            class_def.append(
                type(
                    cls.PrefixNaming + class_base,
                    (base_class,),
                    upmethod,
                )
            )

        cls.__filter.update(default_classes)
        named = [x.Property for x in class_def]
        result = dict(zip(named, class_def))
        # has a default
        result.update({"default": XsceneDefault})
        return result


def __init__(self, name, extra=10):
    print(name, extra)


if __name__ == "__main__":
    assetname = "callan"
    # print(XassetChar(assetname))
    # print(XassetElement(assetname))
    # shotname = "xseq_001"
    # print(Xshot(shotname))

    result = Xscene.context_factory(
        ["Xopinion"],
        base_class=XassetChar,
        upmethod={
            "SHOW_OPINIONS": [
                Modelvariant(assetname, "modeling", "original"),
                Modelvariant(assetname, "surfacing", "original"),
            ],
            "__init__": __init__,
        },
        log=None,
    )
    print(result)
    a = result["Xopinion"](assetname)
    print(a.SHOW_OPINIONS)
    # print(a)
