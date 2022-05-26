import os
import re
from collections import defaultdict
import datetime
import logging

logger = logging.getLogger(__name__)

from meta_io.xml_scene_io import XmlSceneIO
from builders.conf_builder import Configuration
from xcore import xscene
from api.scene_api import write_config, read_config

# def test_all_read():
#     afile = ""
#     all_class_name = xscene.XScene.factory([], None)
#     all_class_name.update(xscene._Generator)
#     print(all_class_name)


# def test_all_read():
#     afile = ""
#     all_class_name = xscene.XScene.factory([], None)
#     all_class_name.update(xscene._Generator)
#     print(all_class_name)

# def test_config_write():
#     aconf = Configuration(None)
#     write_config(aconf.build_from_ymal_config(None))

def test_config_read():
    x = read_config()
    assert x.name == "TOPNODE"
    for y in x.get_children():
        print(x.Property)
        for z in y.get_children():
            print("\t%s" % z.Property)