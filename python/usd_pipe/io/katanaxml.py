# -*- coding: utf-8 -*-

# Local
from usd_pipe.io.genericxml import GenericXml


class KatanaXml(GenericXml):
    @classmethod
    def factory(cls, default_classes, log=None):
        class KatanaDefault(KatanaXml):
            log = None
            __doc__ = ("py representation KatanaDefault",)

        class_def = list()
        for classRoot in default_classes:
            class_def.append(
                type(
                    classRoot + "Xml",
                    (KatanaDefault,),
                    {
                        "log": log,
                        "Property": classRoot,
                        "__doc__": "py representation %s" % classRoot,
                    },
                )
            )

        named = [x.Property for x in class_def]
        result = dict(zip(named, class_def))
        result.update({"default": KatanaDefault})
        return result
