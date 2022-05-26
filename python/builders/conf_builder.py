
from xcore.xscene import (
    XRootEntryAsset,
    XAssetOpinionDesc,
    XAssetOpinionGeom,
    XLayerOther)

from xcore import xscene
from xcore.xscene import XScene

class constant(object):
    configuration = 'Configuration'

class Configuration(XScene):

    Property = "Configuration"
    def __init__(self, tag=None):
        if tag is None:
            tag = constant.configuration
        super(Configuration, self).__init__(tag)
        self.name = "TOPNODE2"


    def build_from_ymal_config(self, confdata):
        entry_e = XRootEntryAsset("elem")
        self.add_child(entry_e)
        for i in range(3):
            x = XAssetOpinionDesc()
            y = XAssetOpinionGeom()
            y.add_child(x)
            entry_e.add_child(y)
        return self

_ConfigurationGen = {
    constant.configuration: Configuration,
}