
from collections import namedtuple



class ConstantInfo(namedtuple("ConstantInfo", "tag Property doc")):
    __slots__ = ()


# schema
class XSceneSchema(object):
    """Collection of ConstantInfo"""
    SDAT = "sda"
    SEP = "_"

    ############################################################################
    # usd layer type
    Layer_Type_layer = ConstantInfo(
        "%s%slayer" % (SDAT, SEP), "layer", "refer a layer type layer"
    )
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
        Layer_Type_layer,
        Layer_Type_payload,
        Layer_Type_reference,
        Layer_Type_sublayer,
        Layer_Type_empty,
    ]

    ############################################################################
    # Base STAGE
    Stage_Type = ConstantInfo(
        "%s%sstage" % (SDAT, SEP), "stage", "can be instanced from a shot"
    )
    Stage_Type_asset = ConstantInfo(
        "%s%sstageasset" % (SDAT, SEP), "stageasset", "can be instanced from a shot"
    )
    Stage_Type_shot = ConstantInfo(
        "%s%sstageshot" % (SDAT, SEP), "stageshot", "collection of animation, location, ligth, camera"
    )
    Stage_Type_seq = ConstantInfo(
        "%s%sstagesequence" % (SDAT, SEP), "stagesequence", "collection of shot"
    )
    Stage_Type_loc = ConstantInfo(
        "%s%sstagelocation" % (SDAT, SEP), "stagelocation", "layout, camera... "
    )
    # a list of base entity definition
    BASE_STAGE = [Stage_Type, Stage_Type_asset, Stage_Type_shot, Stage_Type_seq, Stage_Type_loc]


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
    Opinion_asset = ConstantInfo(
        "%s%sopinion_asset" % (SDAT, SEP), "opinionasset", "type opinion for asset"
    )
    Opinion_asset_desc = ConstantInfo(
        "%s%sopinion_asset_desc" % (SDAT, SEP),
        "descriptionasset",
        "model variant identifier",
    )
    Opinion_asset_geom = ConstantInfo(
        "%s%sopinion_asset_geom" % (SDAT, SEP),
        "geometryasset",
        "the geom identifier",
    )

    OPINION_ASSET = [Opinion_asset, Opinion_asset_desc, Opinion_asset_geom]

    # opinion for shot
    Opinion_shot = ConstantInfo(
        "%s%sopinion_shot" % (SDAT, SEP), "opinionshot", "type opinion for shot"
    )
    Opinion_shot_manifest = ConstantInfo(
        "%s%sopinion_shot_manifest" % (SDAT, SEP),
        "descriptionshot",
        "shot sublayer identifier",
    )
    Opinion_shot_geom = ConstantInfo(
        "%s%sopinion_shot_geom" % (SDAT, SEP), "geometryshot", "the geom identifier"
    )
    # to keep going
    Layer_Type_layer_other = ConstantInfo(
        "%s%sothersubLayer_Type" % (SDAT, SEP), "othersublayer", "other"
    )

    OPINION_SHOT = [Opinion_shot, Opinion_shot_manifest, Opinion_shot_geom]

    OPINIONS = OPINION_ASSET + OPINION_SHOT + [Layer_Type_layer_other]

    _all__ = USD_LAYERS + BASE_STAGE + ENTRIES_LAYER  + OPINIONS
