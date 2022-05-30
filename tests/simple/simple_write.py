import os
import sys
import re
from collections import defaultdict
import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)

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

def test_config_write():
    aconf = Configuration(None)
    write_config(aconf.build_from_ymal_config(None),"toto2.xml")

def test_config_read():
    x = read_config("toto2.xml")
    x.set_log(logger)
    x.set_filter(['sda_opinion_asset_geom', 'sda_opinion_asset_desc','Configuration'])
    assert x.name == "TOPNODE2"
    x.print_nice()
    for y in x.get_children():
        print(y.Property)
        for z in y.get_children():
            # print(type(z.fields),z.fields)
            print("\t%s" % z.Property)
            for k in z.get_children():
                print("\t\t%s" % k.Property)
                print("\t\t\t%s" % k.get_children())
                for x in k.get_children():
                    print(x.decode_value())
                