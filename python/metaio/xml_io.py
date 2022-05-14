# -*- coding: utf-8 -*-
import re
import logging
import xml.dom
from xml.sax.saxutils import escape, unescape
import xml.etree.cElementTree as ET


class XmlIO(object):
    log = None

    _xml_special_chars = {
        "<": "&lt;",
        ">": "&gt;",
        "'": "&apos;",
        '"': "&quot;",
    }
    _xml_special_chars_re = re.compile("({})".format("|".join(_xml_special_chars)))

    def __init__(self):
        self._dom = None

    def reset(self):
        if self._dom is not None:
            self._dom.unlink()
        self._dom = None

    def create_dom(self):
        self.reset()
        self._dom = xml.dom.getDOMImplementation().createDocument(None, None, None)
        return self._dom

    @classmethod
    def escape_special_chars(cls, astr):
        return cls._xml_special_chars_re.sub(
            lambda match: cls._xml_special_chars[match.group(0)], astr
        )

    @staticmethod
    def do_escape(astr):
        return escape(astr)

    @staticmethod
    def do_unescape(astr):
        return unescape(astr)

    @classmethod
    def set_log(cls, log=None):
        """
        Args:
            log(logging handler): use by all instances
        """
        if cls.log is None and log is None:
            cls.log = logging.getLogger(__name__)
        else:
            cls.log = log

    def recurse_instance_xml(self, instance, all_class_dict, root=None):
        """Instanciate a node for each element. Traverse the tree
        Args:
            instance(xmlelement):
        """
        anode = None
        if instance is None:
            return None

        if instance.tag in all_class_dict:
            anode = all_class_dict[instance.tag](tag=instance.tag)
            anode.set_attribute_xml(instance)
        else:
            # wrap  scenegraphXML
            atype = instance.get("baseType")
            if atype is None:
                atype = instance.get("type")
            if atype is None:
                atype = instance.tag

            if atype in all_class_dict:
                anode = all_class_dict[atype](tag=instance.tag)
                anode.set_attribute_xml(instance)
            else:
                if self.log:
                    if atype is not None:
                        self.log.warning("not found {}".format(atype))
                    else:
                        raise Exception("None value")
                anode = all_class_dict["default"](tag=instance.tag)
                anode.set_attribute_xml(instance)

        if root is None:
            root = anode
        children = list()
        for inst in instance.getchildren():
            ch = self.recurse_instance_xml(inst, all_class_dict, root)
            if ch is not None:
                children.append(ch)
        if len(children) > 0:
            anode.set_children(children, root)
        return anode

    @staticmethod
    def deserialize(astr):
        return ET.ElementTree(ET.fromstring(astr))
