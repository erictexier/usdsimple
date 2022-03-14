# -*- coding: utf-8 -*-
from pprint import pformat
import collections
import logging

# Local
from usd_pipe.io.xml_io import XmlIO
class GenericXml(object):
    __slots__ = ["__children", "__parent", "__verbose", "__xmltag"]
    Property = "GenericXml"
    log = None
    __factory = {}

    def __init__(self, tag=None):
        super(GenericXml, self).__init__()
        assert tag is not None
        self.__children = []
        self.__verbose = True
        self.__parent = None
        self.__xmltag = tag

    @classmethod
    def factory(cls, default_class, log=None):
        raise Exception("factory is needed")

    @classmethod
    def set_factory(cls, factory):
        cls.__factory = factory

    def serialize(self, with_children=False):
        """
        Returns:
            string(xml)
        """
        wio = XmlIO()
        dom = wio.create_dom()
        elmt = self.to_xml_element(dom, dom)
        if with_children:
            self.toxml_children(dom, elmt)
        res = elmt.toxml()
        wio.reset()
        return res

    @classmethod
    def deserialize(cls, astringxml):
        """"""
        assert cls.__factory
        rio = XmlIO()
        xmltree = rio.deserialize(astringxml)
        root = xmltree.getroot()
        ret = rio.recurse_instance_xml(xmltree.getroot(), cls.__factory)
        return ret

    @classmethod
    def set_log(cls, log=None):
        """
        Args:
            log(logging handle): use by all instances
        """
        if cls.log is None and log is None:
            cls.log = logging.getLogger(__name__)
        else:
            cls.log = log

    def set_parent(self, parent):
        self.__parent = parent

    def get_parent(self):
        return self.__parent

    def get_children(self):
        return self.__children

    def set_children(self, children, root=None):
        assert isinstance(children, list)
        if children is not None:
            self.__children = children
        for ch in children:
            ch.set_parent(self)
            if root:
                ch.register(root)

    def add_child(self, ch):
        if ch == None:
            return False
        if self.__children == None:
            self.__children = list()
        self.__children.append(ch)
        ch.set_parent(self)
        return True

    def register(self, root=None):
        pass

    def get_register(self):
        return list()

    def to_xml_element(self, dom, parent_elmt):
        """Creates element and set attribute inside of parent and returns it
        Args:
            parent_elmt(element): the parent node
        Returns:
            xml element
        """
        tag = self.get_tag()
        if tag is None:
            # None serialized
            return None
        self.before_to_xml()
        element = dom.createElement(self.get_tag())
        if parent_elmt:
            parent_elmt.appendChild(element)

        attr = dict()
        attr.update(self.__dict__)

        for key in attr:
            if key.startswith("_"):
                key, value = self.to_key_value(key)
            else:
                value = str(attr[key])
            if key != "":
                value = XmlIO.do_escape(value)
                value = value.replace("\n", "&#0010;")
                value = XmlIO.escape_special_chars(value)
                element.setAttribute(key, value)
        self.post_to_xml()
        return element

    def before_to_xml(self):
        # this is a method that can be overwriten to check valid and format for xml
        pass

    def post_to_xml(self):
        # same as before_to_xml, after xml element has been set
        pass

    def to_key_value(self, key=None):
        """ mapping key, value for saving in xml """
        return "", None

    def get_tag(self):
        return self.__xmltag

    def toxml_children(self, dom, element):
        for ch in self.__children:
            node = ch.to_xml_element(dom, element)
            ch.toxml_children(dom, node)

    def set_attribute_xml(self, element):
        if element.attrib is not None:
            for key in element.attrib:
                self.__dict__[key] = XmlIO.do_unescape(element.attrib[key])

    def print_nice(self, max_char=120, tab=""):
        """Print out node on line with the tag name and recursively the children
        Args:
            max_char(int): clip the value of attrib
            tab(string): indent
        """
        d = collections.OrderedDict()
        for key in self.__dict__:
            if key.startswith("_"):
                continue
            if len(self.__dict__[key]) > max_char:
                d.update({key: self.__dict__[key][:max_char] + " ..."})
            else:
                d.update({key: self.__dict__[key]})

        info = "{} {}: {}".format(
            tab, self.Property, pformat(d).replace("OrderedDict([", "")[:-2],
        )
        if self.log is not None and self.__verbose == True:
            self.log.info(info)
        for ch in self.__children:
            ch.print_nice(max_char=max_char, tab=tab + " " * 4)

    # def __repr__(self):
    #    return "{}: {}".format(self.Property, pformat(self.__dict__, indent=4))

    @property
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, verbose):
        self.__verbose = verbose
