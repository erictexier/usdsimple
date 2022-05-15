
from collections import namedtuple

from ucore.xroot import XRootEntry
from ucore.xroot import XAssetOpinion
from ucore.xroot import XShotOpinion


class XSchema(namedtuple("XSchema", "tag generator data")):
    __slots__ = ()

class SchemaEntry(object):

    SHOT = XSchema("SHOT", XRootEntry, {})
    ELEM = XSchema("ELEM", XRootEntry, {})
    CHAR = XSchema("CHAR", XRootEntry, {})
    SEQ = XSchema("SEQ", XRootEntry, {})
    LOC = XSchema("LOC", XRootEntry, {})

class SchemaAssetEntrySubLayer(object):
    OPINION_ASSET_CHAR = XSchema("OPINION_ASSET_CHAR", XAssetOpinion, {})
    OPINION_ASSET_ELEM = XSchema("OPINION_ASSET_ELEM", XAssetOpinion, {})

class SchemaShotEntrySubLayer(object):
    OPINION_SHOT_GEOM = XSchema("OPINION_SHOT_GEOM", XShotOpinion, {})
    OPINION_SHOT_MANIFEST = XSchema("OPINION_SHOT_MANIFEST", XShotOpinion, {})
