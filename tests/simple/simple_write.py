import os
import re
from collections import defaultdict
import datetime
import logging

logger = logging.getLogger(__name__)

from meta_io.xml_scene_io import XmlSceneIO
from xcore import xscene


def test_all_read():
    afile = ""
    all_class_name = xscene.XScene.factory([], None)
    all_class_name.update(xscene._Generator)
    print(all_class_name)


def test_all_read():
    afile = ""
    all_class_name = xscene.XScene.factory([], None)
    all_class_name.update(xscene._Generator)
    print(all_class_name)
