# -*- coding: utf-8 -*-


import os
import re
import shutil
import tempfile
import tarfile

import xml.etree.cElementTree as ET

# local
from dsk.base.utils import disk_utils
from usd_pipe.io.xml_io import XmlIO


class XmlKatanaIO(XmlIO):
    @staticmethod
    def _split_header(aline):
        """handle the first line
        Args:
            aline(str): header line of any katana file
        Returns:
            str: header
        """
        result = dict()
        aline = aline.replace("<katana", "")
        aline = aline.replace(">", "")
        aline = aline.split()
        for expr in aline:
            expr = expr.split("=")
            if len(expr) == 2:
                result[expr[0]] = expr[1].replace('"', "")
        return result

    @staticmethod
    def _to_headerline(pyobj, tag):
        """build the headerline from pyobj
        Args:
            pyobj(object):
        Results:
            str: header line
        """
        result = list()
        result.append("<%s" % tag)
        if hasattr(pyobj, "__dict__"):
            for x in pyobj.__dict__:
                result.append('%s="%s"' % (x, pyobj.__dict__[x]))
        return " ".join(result) + ">"

    def _katana_readxml(self, katana_file):
        """Parse katana and livegroup file
        Args:
            katana_file(str): a file with an katana extension
        Returns:
            first_element, child root
        """
        if not os.path.exists(katana_file):
            return None, None
        xmltree = None
        if katana_file.endswith(".katana"):
            with open(katana_file, "r:gz") as k:
                lines = k.readlines()
                first_line = lines[0]
                if 'archive="tar"' in first_line:
                    a_temp_dir = tempfile.mkdtemp()
                    dummy = os.path.join(a_temp_dir, "dummy.gzip")
                    with open(dummy, "wb") as bf:
                        bf.writelines(lines[1:])
                    # extract/dump the tarfile
                    with tarfile.open(dummy, "r") as tf:
                        # with suppose only one file for now
                        filename = tf.getnames()[0]
                        tf.extract(filename, a_temp_dir)
                        new_lines = list()
                        name_to_read = os.path.join(a_temp_dir, filename)
                        xmltree = ET.parse(name_to_read)
                    shutil.rmtree(a_temp_dir)
                    attrs = self._split_header(first_line)

                    aline = first_line.replace(">", "</katana>")
                    aline = aline.replace("<katana", "<katana>")
                    root = ET.Element("katana")

                    for atrib in attrs:
                        root.set(atrib, attrs[atrib])
                    return root, xmltree.getroot()
                else:
                    xmltree = ET.parse(katana_file)
                    return None, xmltree.getroot()
        else:
            # support for livegroup
            xmltree = ET.parse(katana_file)
        if xmltree is None:
            return None, None
        return None, xmltree.getroot()

    def write_katana(self, node, katana_file_out, do_zip=True):
        """Write katana and livegroup file
        Args:
            node(KatanaXml): the top node to start the save
            katana_file(str): a file with an katana extension
            do_zip(boolean): true, gzip compression
        Returns:
            boolean: True if success
        """
        dom = self.create_dom()
        if do_zip:
            first_line = cls._to_headerline(node, node.get_tag())
            try:
                node = node.get_children()[0]
            except:
                return False
            elmt = node.to_xml_element(dom, dom)
            node.toxml_children(dom, elmt)
            a_temp_dir = tempfile.mkdtemp()
            scene = "scene.katana"
            sub_temp_dir = os.path.join(a_temp_dir, "scene")
            disk_utils.DiskUtils.create_path(sub_temp_dir)
            sub_temp_file = os.path.join(sub_temp_dir, scene)
            out_temp_tarfile = os.path.join(a_temp_dir, "dummy.gzip")
            archname = os.path.join("scene", scene)

            with open(sub_temp_file, "wb") as fout:
                elmt.writexml(fout, "\n", " " * 2)

            # this is ugly, in progress
            with open(sub_temp_file, "rb") as fin:
                lines = fin.readlines()
                lines = [x.rstrip() for x in lines]
                lines = filter(None, lines)
                lines = [x.replace("&amp;amp;", "&") for x in lines]
                lines = [x.replace("&amp;", "&") for x in lines]

                with open(sub_temp_file, "wb") as fout:
                    fout.write("\n".join(lines))
            with tarfile.open(out_temp_tarfile, mode="w:gz") as fout:
                fout.add(sub_temp_file, arcname=archname, recursive=False)

            with open(katana_file_out, "wb") as fout:
                fout.write(first_line + "\n")
                with open(out_temp_tarfile, "rb") as dfile:
                    fout.writelines(dfile.readlines())
            shutil.rmtree(a_temp_dir)
        else:
            elmt = node.to_xml_element(dom, dom)
            node.toxml_children(dom, elmt)
            with open(katana_file_out, "w") as fout:
                elmt.writexml(fout, "\n", " " * 2)

            # this is ugly, in progress
            with open(katana_file_out, "r") as fin:
                lines = fin.readlines()
                lines = [x.rstrip() for x in lines]
                lines = filter(None, lines)
                lines = [x.replace("&amp;amp;", "&") for x in lines]
                lines = [x.replace("&amp;", "&") for x in lines]

                with open(katana_file_out, "w") as fout:
                    fout.write("\n".join(lines))
        self.reset()
        return True

    @classmethod
    def read_katana(cls, katana_file, factory):
        """Read a katana or livegroup, and return top node:
        tag or type are getting instanciate according to the factory dict

        Args:
            katana_file(str): katana or livegroup extension
            factory(dict): str -> subclass of KatanaXml
        Returns:
            subclass of KatanaXml
        """
        rio = XmlKatanaIO()
        xmlroot, data = rio._katana_readxml(katana_file)
        top = None
        child = None
        if xmlroot is not None:
            top = rio.recurse_instance_xml(xmlroot, factory)
        if data is not None:
            child = rio.recurse_instance_xml(data, factory)
        if child is not None:
            if top is not None:
                top.add_children([child])
            else:
                top = child
        rio.reset()
        return top
