from usd_pipe.usd.core.xroot import XassetChar

# from . import xroot
print(xroot.XassetChar("toto"))

class_serialize = object


class Xscene(class_serialize):
    Property = "Xscene"
    PrefixNaming = "X"

    def __init__(self, tag=None):
        super(Xscene, self).__init__()
        self.tag = tag

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
        result.update({"default": XSceneDefault})
        return result
