from ucore.xschema import XRootEntry
from ucore.xschema import XAssetOpinion
from ucore.xschema import XShotOpinion
from ucore.xschema import XSeqLayer
from ucore.xschema import XLocLayer


class XSchema(namedtuple("XSchema", "tag generator data")):
    __slots__ = ()

class SchemaEntry(object):

    SHOT = XSchema("SHOT", XRootEntry, {})
    ELEM = XSchema("ELEM", XRootEntry, {'is_prop': True})
    CHAR = XSchema("CHAR", XRootEntry, {'is_prop': False})
    SEQ = XSchema("SEQ", XRootEntry, {})
    LOC = XSchema("LOC", XRootEntry, {})



class SchemaAssetEntrySubLayer(object):
    OPINION_ASSET_CHAR = XSchema("OPINION_ASSET_CHAR", XAssetOpinion, {})
    OPINION_ASSET_ELEM = XSchema("OPINION_ASSET_ELEM", XAssetOpinion, {})

class SchemaShotEntrySubLayer(object):
    OPINION_SHOT = XSchema("OPINION_SHOT", XShotOpinion, {})
    SUBLAYER_SEQ = XSchema("SUBLAYER_SEQ", XSeqLayer, {})
    SUBLAYER_LOC = XSchema("SUBLAYER_LOC", XLocLayer, {})


class Asset(SchemaEntry):
    def __init__(self, name, asset_type, ctx):
        if asset_type == 'ELEM':
            self._asset = self.ELEM.generator()
        else:
            self._asset = self.CHAR.generator()
        self._asset.set_children(ctx.get_opinion())