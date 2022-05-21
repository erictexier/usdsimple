
from collections import namedtuple



class ConstantInfo(namedtuple("ConstantInfo", "tag Property doc")):
    __slots__ = ()


# schema
class XSceneSchema(object):
    """Collection of ConstantInfo"""
    SDAT = "sda"
    SEP = "::"

    ############################################################################
    # usd layer type
    Layer_Type_payload = ConstantInfo(
        "%s%spayload" % (SDAT, SEP), "payload", "refer a payload type layer"
    )
    Layer_Type_reference = ConstantInfo(
        "%s%sreference" % (SDAT, SEP), "reference", "refer a reference type layer"
    )
    Layer_Type_sublayer = ConstantInfo(
        "%s%ssublayer" % (SDAT, SEP), "sublayer", "refer a sublayer type layer"
    )
    Layer_Type_empty = ConstantInfo(
        "%s%sempty" % (SDAT, SEP), "empty", "refer to an empty layer"
    )

    # a list of usd layer type definition
    USD_LAYERS = [
        Layer_Type_payload,
        Layer_Type_reference,
        Layer_Type_sublayer,
        Layer_Type_empty,
    ]

    ############################################################################
    # Base GEOM
    Layer_Type_asset = ConstantInfo(
        "%s%sasset" % (SDAT, SEP), "asset", "can be instanced from a shot"
    )
    Layer_Type_shot = ConstantInfo(
        "%s%sshot" % (SDAT, SEP), "shot", "collection of animation, location, ligth, camera"
    )
    Layer_Type_seq = ConstantInfo(
        "%s%ssequence" % (SDAT, SEP), "sequence", "collection of shot"
    )
    Layer_Type_loc = ConstantInfo(
        "%s%slocation" % (SDAT, SEP), "location", "layout, camera... "
    )
    # a list of base entity definition
    BASE_GEOM_LAYER = [Layer_Type_asset, Layer_Type_shot, Layer_Type_seq, Layer_Type_loc]


    ############################################################################
    # entry
    Entry_Type = ConstantInfo(
        "%s%sentry" % (SDAT, SEP), "entry", "list of option with or without usd prim"
    )

    # entry
    Entry_Type_asset = ConstantInfo(
        "%s%sentryasset" % (SDAT, SEP), "entryasset", "list of option with or without usd prim"
    )

    # entry
    Entry_Type_shot = ConstantInfo(
        "%s%sentryshot" % (SDAT, SEP), "entryshot", "list of option with or without usd prim"
    )

    # entry
    Entry_Type_seq = ConstantInfo(
        "%s%sentrysequence" % (SDAT, SEP), "entrysequence", "list of option with or without usd prim"
    )

    # entry
    Entry_Type_loc = ConstantInfo(
        "%s%sentrylocation" % (SDAT, SEP), "entrylocation", "list of option with or without usd prim"
    )
    ENTRIES_LAYER = [Entry_Type, Entry_Type_asset, Entry_Type_shot, Entry_Type_seq, Entry_Type_loc]


    ############################################################################
    # SUBLAYERS
    # opinion for asset
    opinion_asset = ConstantInfo(
        "%s%sopinion_asset" % (SDAT, SEP), "opinionasset", "type opinion for asset"
    )
    opinion_asset_desc = ConstantInfo(
        "%s%sopinion_asset_desc" % (SDAT, SEP),
        "descriptionasset",
        "model variant identifier",
    )
    opinion_asset_geom = ConstantInfo(
        "%s%sopinion_asset_geom" % (SDAT, SEP),
        "geometryasset",
        "the geom identifier",
    )

    OPINION_ASSET = [opinion_asset, opinion_asset_desc, opinion_asset_geom]

    # opinion for shot
    opinion_shot = ConstantInfo(
        "%s%sopinion_shot" % (SDAT, SEP), "opinionshot", "type opinion for shot"
    )
    opinion_shot_manifest = ConstantInfo(
        "%s%sopinion_shot_manifest" % (SDAT, SEP),
        "descriptionshot",
        "shot sublayer identifier",
    )
    opinion_shot_geom = ConstantInfo(
        "%s%sopinion_shot_geom" % (SDAT, SEP), "geometryshot", "the geom identifier"
    )
    # sublayer
    other_Layer_Type = ConstantInfo(
        "%s%sothersubLayer_Type" % (SDAT, SEP), "othersublayer", "other"
    )
    OPINION_SHOT = [opinion_shot, opinion_shot_manifest, opinion_shot_geom]

    _all__ = USD_LAYERS + BASE_GEOM_LAYER + ENTRIES_LAYER  + OPINION_ASSET + OPINION_SHOT + [other_Layer_Type]
