
from xcore.xscene import (
    XRootEntryAsset,
    XAssetOpinionDesc,
    XAssetOpinionGeom,
    FieldsInstance,
    InstanceAttrib,
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
        entry_e = XRootEntryAsset()
        self.add_child(entry_e)
        for i in range(3):
            x = XAssetOpinionDesc()
            ai = InstanceAttrib()
            ai.set_data_with_type({'name': 'anewname', 'value' : {'[gabc]': '.abc', '[geovar]' : 'model'}})
            x.add_child(ai)
            y = XAssetOpinionGeom()
            if i==2:
                print("oops")
                y.set_fields({'toto': 3, 'tata': 'somedata'})
                y.name = "withfield"
            y.add_child(x)
            entry_e.add_child(y)
            at = FieldsInstance()
            at.set_key("toto%d" % i)
            y.add_child(at)
        return self

_ConfigurationGen = {
    constant.configuration: Configuration,
}