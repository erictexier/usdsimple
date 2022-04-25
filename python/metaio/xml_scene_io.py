# -*- coding: utf-8 -*-
import os
import re
import shutil
import tempfile
import tarfile
import json

import xml.etree.cElementTree as ET

# local
from dsk.base.utils import disk_utils
from usd_pipe.io.xml_io import XmlIO


class XmlSceneIO(XmlIO):
    @classmethod
    def write_scene(cls, node, scene_file_out):
        """Write scene file
        Args:
            node(SceneXml): the top node to start the save
            scene_file(str): a file with an scene extension
        Returns:
            boolean: True if success
        """
        wio = cls()
        dom = wio.create_dom()
        elmt = node.to_xml_element(dom, dom)
        node.toxml_children(dom, elmt)
        with open(scene_file_out, "w") as fout:
            # elmt.writexml(fout, "", "")
            # nicer
            elmt.writexml(fout, "\n", " " * 2)
        wio.reset()
        return True

    @classmethod
    def read_scene(cls, scene_file, factory):
        """Read a scene, and return top node:
        tag or type are getting instanciate according to the factory dict

        Args:
            scene_file(str): scene extension
            factory(dict): str -> subclass of SceneXml
        Returns:
            subclass of SceneXml
        """
        if not os.path.exists(scene_file):
            return None
        xmltree = ET.parse(scene_file)
        rio = cls()
        ret = rio.recurse_instance_xml(xmltree.getroot(), factory)
        rio.reset()
        return ret

    @staticmethod
    def read_from_json(json_file):
        """
        Args:
            json_file(str): json file
        Returns:
            dict()
        """
        data_all = dict()
        try:
            with open(json_file, "r") as f:
                data_all = json.load(f)
        except Exception as e:
            print("Error Reading the manifest: {}".format(e))
        return data_all
