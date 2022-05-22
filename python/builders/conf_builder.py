
from python.xcore.xscene import XRootEntryAsset
from xcore.xscene import XScene
class constant(object):
    """
    """

    # for scenegraph
    configuration = "Configuration"


class Configuration(XScene):

    Property = "Configuration"
    def __init__(self, tag=None):
        if tag is None:
            tag = constant.configuration
        super(Configuration, self).__init__(tag)


    def build_from_ymal_config(self, confdata):
        entry_e = XScene.XRootEntryAsset(confdata.ELEM)
        self.add_child(entry_e)




_Generator = {

}

_Generator.update(Configuration.get_factory())