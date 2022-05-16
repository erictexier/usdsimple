
from collections import namedtuple



class ConstantInfo(namedtuple("ConstantInfo", "tag type doc")):
    __slots__ = ()


# schema
class XSceneSchema(object):
    """Collection of ConstantInfo"""
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

    # a list of usd layer type definition
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

    # a list of base entity definition
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
        "model variant identifier",
    )
    opinion_asset_geom = ConstantInfo(
        "%s%sopinion_asset_geom" % (SDAT, SEP),
        "geometryasset",
        "the geom identifier",
    )

    # opinion for shot
    opinion_shot = ConstantInfo(
        "%s%sopinion_shot" % (SDAT, SEP), "opinionshot", "type opinion for shot"
    )
    opinion_shot_manifest = ConstantInfo(
        "%s%sopinion_shot_manifest" % (SDAT, SEP),
        "descriptionshot",
        "model variant identifier",
    )
    opinion_shot_geom = ConstantInfo(
        "%s%sopinion_shot_geom" % (SDAT, SEP), "geometryshot", "the geom identifier"
    )

    # sublayer
    other_layer_type = ConstantInfo(
        "%s%ssublayer_type" % (SDAT, SEP), "sublayer", "other"
    )

    sda_type_all = [
        entry_type,
        opinion_asset,
        opinion_asset_desc,
        opinion_asset_geom,
        opinion_shot,
        opinion_shot_manifest,
        opinion_shot_geom,
        other_layer_type,
    ]

    _all__ = usd_layer_types + basic_types + sda_type_all
