
from collections import namedtuple
from ucore.xroot import XRootEntry

class XSchema(namedtuple("XSchema", "tag generator data")):
    __slots__ = ()

class SchemaEntry(object):

    SHOT = XSchema("SHOT", XRootEntry, {})
    ELEM = XSchema("ELEM", XRootEntry, {})
    CHAR = XSchema("CHAR", XRootEntry, {})
    SEQ = XSchema("SEQ", XRootEntry, {})
    LOC = XSchema("LOC", XRootEntry, {})

