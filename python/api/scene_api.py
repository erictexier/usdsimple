# -*- coding: utf-8 -*-
import os
import re
from collections import defaultdict
import datetime
import logging
logger = logging.getLogger(__name__)

from meta_io.xml_scene_io import XmlSceneIO
from xcore.xscene import XScene
#from xcore.xscene import FromSptConfig
from xcore.xscene import xconstant, _XGen
from builders.conf_builder import _ConfigurationGen


""" 
Warning: This api does deal with existance for file, I will mostly crash
         if resource are unavailable.
Todo: build documented exception in xml_io
"""
class SchemaScene(object):
    """not very consistant but should match bm manifest"""

    schema_scene = {
        "Animations": "animation",
        "Camera": "camera",
        "Layout": "layout",
        "Crowds": "crowds",
        "Grass": "grass",
        "Scatter": "scatter",
        "Fx": "fx",
    }
    """ for any key value for result of scanning """
    animation = schema_scene["Animations"]
    camera = schema_scene["Camera"]
    layout = schema_scene["Layout"]
    crowds = schema_scene["Crowds"]
    grass = schema_scene["Grass"]
    scatter = schema_scene["Scatter"]
    fx = schema_scene["Fx"]

    """ label are the header key in manifest """
    animation_label = "Animations"
    camera_label = "Camera"
    layout_label = "Layout"
    crowds_label = "Crowds"
    grass_label = "Grass"
    scatter_label = "Scatter"

    scatterasset_label = "_ScatterAsset"
    scattershot_label = "_ScatterShot"
    fx_label = "Fx"

    # to extract scene for scanning
    scenegraph_label = "scenefile"
    topnode_label = "root_node"
    token_label = "node_name"


####
def write_config(topnode, scene_out="toto.xml"):
    if not XmlSceneIO.write_scene(topnode, scene_out):
        logger.error("ERROR saving")
    else:
        logger.error("{} saved".format(scene_out))

def read_config(scene_in="toto.xml"):
    all_class_name = XScene.factory([], None)

    # all_class_name.update(_XGen)
    all_class_name.update(_ConfigurationGen)
    return XmlSceneIO.read_scene(scene_in, all_class_name)

#####
def read_scenegraph(layout_file):
    """basic layout with no support (see XScene for minimun api)
    Can be sufficient, for xml basic things like serialize 
    """
    all_class_name = XScene.factory([], None)
    return XmlSceneIO.read_scene(layout_file, all_class_name)


def write_scenegraph(topnode, scene_out):
    assert topnode.get_tag() == "scenegraphXML"
    if not XmlSceneIO.write_scene(topnode, scene_out):
        logger.error("ERROR saving")
    else:
        logger.error("{} saved".format(scene_out))


#####
def read_scene(scene_file, ctx=None):
    """ Read xml scenegraph (with tag: 'instance', 'arbitraryList')
    Args:
        scene_file(str): filename of any scenegraph
    """
    all_class_name = XScene.factory([], None)
    all_class_name.update(scenexml._Generator)
    if ctx:
        ScenegraphXml.set_bams(SceneBams(ctx))

    node = XmlSceneIO.read_scene(scene_file, all_class_name)
    """
    try:
        node.update_subregion()
    except Exception as e:
        raise Exception("Wrong Api: {}".format(e))
    assert node.get_tag() == "scenegraphXML"
    return node
    """

#####
def read_full_shot(scene_file, ctx=None):
    """ Same read scene, but only scenegraphXML3D
    Args:
        scene_file(str): filename of any scenegraph
        ctx(context): if None, no bams support
    Returns:
        scenegraphXML3D instance
    """
    all_class_name = XScene.factory([], None)
    all_class_name.update(scenexml._Generator)
    if ctx:
        ScenegraphXml.set_bams(SceneBams(ctx))

    node = XmlSceneIO.read_scene(scene_file, all_class_name)
    try:
        node.update_subregion()
    except Exception as e:
        raise Exception("Wrong Api: {}".format(e))
    assert node.get_tag() == constant.scenetag
    return node



#####
def write_scene(topnode, scene_out):
    """write scene graph with animation, camera..."""
    assert topnode.get_tag() == constant.scenetag
    if not XmlSceneIO.write_scene(topnode, scene_out):
        logger.error("ERROR saving")
        return False
    else:
        logger.info("{} saved".format(scene_out))
    return True


#####
def write_scene_with_header(topnode, scene_out, in_scene=""):
    """Mark the top header line with the scene it was made from"""
    topnode.from_scene = in_scene
    topnode.date_created = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return write_scene(topnode, scene_out)


