# -*- coding: utf-8 -*-
import os
import re
from collections import defaultdict
import datetime
import logging
logger = logging.getLogger(__name__)

from meta_io.xml_scene_io import XmlSceneIO
from xcore.xscene import XScene
from xcore.xscene import FromSptConfig
from xcore.xscene import constant


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


#####
def get_header_info(ascene):
    """take advantage for now that this is not compress
    parse the first line of the file and return a dict
    """
    result = dict()
    try:
        with open(ascene, "r") as fin:
            line = fin.readline()
            # there is blank line sometime. probably the missing xml standard line
            if line == "\n":
                line = fin.readline()
            line = line.strip()
            fields = line.split(" ")
            for field in fields:
                if "=" in field:
                    xx = field.split("=")
                    if len(xx) == 2:
                        result[xx[0]] = xx[1].replace('"', "")
    except:
        pass
    return result



#####################################
class SceneBuilder(object):
    """ Scanner for manifest and scenegraph (use also in katana_klf) with no needs 
        for material wired in katana, base class for 
    """

    _pat_crowd = re.compile("_crowdField[\d]+_loader")
    _crowd_sep = ";"

    def __init__(self):
        self.avoid_twice_mtl_export = set([])

    @classmethod
    def scenegraph_scan(cls, in_scene):
        """
        Args:
            in_scene(str): a scene from xml
        Returns:
            defaultdict(list): key: layout, camera ..., list of scene element
        """
        # LAYOUT
        topnode = read_scene(in_scene)
        name = os.path.basename(in_scene)
        return {
            SchemaScene.token_label: name,
            SchemaScene.scenegraph_label: in_scene,
            SchemaScene.topnode_label: topnode,
        }

        return result

    @classmethod
    def manifest_scan(cls, in_scene):
        """
        Args:
            in_scene(str): a scene from json
        Returns:
            defaultdict(list): key: layout, camera ..., list of scene element
        """
        result = read_manifest(in_scene)
        return result

    @classmethod
    def katana_scan(cls, in_scene):
        """
        Args: method that will be overwrite in katana
            in_scene(str): a scene from katana, livegroup
        Returns:
            defaultdict(list): key: layout, camera ..., list of scene element
        """
        raise Exception("No support outside katana_klf")

        return defaultdict(list)

    def load_and_process(self, ctx, in_scene, material, outdir, scanner, force):
        """ IN PROGRESS same as klf_katana"""

        self.avoid_twice_mtl_export = set([])

        # manage file naming to help: need an other place
        from usd_pipe.usd.usdfile_utils import UsdFileUtils

        do_material = UsdFileUtils.do_material(material)
        # class variable to avoid double export of mtl

        is_katana = (
            True
            if (in_scene.endswith(".katana") or in_scene.endswith(".livegroup"))
            else False
        )
        if is_katana:
            result = self.katana_scan(in_scene)
        else:
            is_xml = True if in_scene.endswith(".xml") else False
            if is_xml:
                # to match when multiple scenegraph]
                result = defaultdict(list)
                result[SchemaScene.layout].append(self.scenegraph_scan(in_scene))
            else:
                is_json = True if in_scene.endswith(".json") else False
                if is_json:
                    result = self.manifest_scan(in_scene)

        helper = UsdFileUtils(ctx, outdir, logger)

        # That should be move else where
        # done with basic scanning, build out scene with material
        master = UsdFileUtils.get_scene_header_node("from_katana", material)
        container_world = XScene(
            constant.attrlist
        )  # should be a list or directly master child
        container_world.name = "World"
        master.add_child(container_world)

        scene_files = list()

        material_list = list()
        if result[SchemaScene.layout]:
            # the layout here is already a scene, we just move the data to a new head
            # and add material if needed
            container_layout = XScene(constant.attrlist)
            container_layout.name = SchemaScene.layout_label
            container_world.add_child(container_layout)
            for asset in result[SchemaScene.layout]:
                scene_files.append(asset[SchemaScene.scenegraph_label])
                sgr_node = asset[SchemaScene.topnode_label]
                geomlist = sgr_node.get_register()["GEOM_3D"]
                tmplist = list()
                if do_material:
                    # scanner klf
                    material_list.extend(
                        [(geom, scanner.scan_material(geom)) for geom in geomlist]
                    )
                regions = sgr_node.get_register()["REGION_3D"]
                if len(result[SchemaScene.layout]) > 1:
                    for x in regions:
                        x.name = "%s:%s" % (asset[SchemaScene.token_label], x.name)
                container_layout.set_children(regions)

        # Camera
        if result[SchemaScene.camera]:
            container_camera = XScene(constant.attrlist)
            container_camera.name = SchemaScene.camera_label
            container_world.add_child(container_camera)
            container_camera.set_children(result[SchemaScene.camera])

        # Anim
        if result[SchemaScene.animation]:
            container_anim = XScene(constant.attrlist)
            container_anim.name = SchemaScene.animation_label
            container_world.add_child(container_anim)
            if do_material:
                material_list.extend(
                    [
                        (geom, scanner.scan_material(geom))
                        for geom in result[SchemaScene.animation]
                    ]
                )
            container_anim.set_children(result[SchemaScene.animation])

        # Crowds
        if result[SchemaScene.crowds]:
            if do_material:
                material_list.extend(
                    [
                        (geom, scanner.scan_material(geom))
                        for geom in result[SchemaScene.crowds]
                    ]
                )
            split_crowds = defaultdict(list)
            for i, node_crowd in enumerate(result[SchemaScene.crowds]):
                group = node_crowd.name.split(self._crowd_sep)
                split_crowds[group[1]].append(node_crowd)

            container_crowds = XScene(constant.attrlist)
            container_crowds.name = SchemaScene.crowds_label
            for crowds_bunch in split_crowds:
                container_bunch = XScene(constant.attrlist)
                container_bunch.name = crowds_bunch
                container_crowds.add_child(container_bunch)
                container_crowds.set_children(split_crowds[crowds_bunch])
            container_world.add_child(container_crowds)

        # scatter
        if result[SchemaScene.scatter]:
            container_scatter = XScene(constant.attrlist)
            container_scatter.name = SchemaScene.scatter_label
            container_world.add_child(container_scatter)
            for i, node in enumerate(result[SchemaScene.scatter]):
                # the scene graph as the bams service, we register to query bams
                # for sub asset in the scatter file
                node.register(master)
                assetnode = node.set_primary_dependency()
                if do_material:
                    material_list.extend(
                        [(geom, scanner.scan_material(geom)) for geom in assetnode]
                    )
            container_scatter.set_children(result[SchemaScene.scatter])

        # build materials
        self.set_mtl(material_list, material, helper, force)

        helper.save_scene(master, in_scene, force)
        return True

    @classmethod
    def set_mtl(cls, material_list, key_mat, helper, force=False):
        """ In progress:
            save material on node as encoded in the scene
            Use the base name of the assiated klf and some subproject path
            see: usd_pipe.usd UsdFileUtils
        Args:
            material_list(tupple): XScene instance,  dict (mat)
            key_mat(str): helper.file_mat or helper.embedded_mat
            helper(UsdFileUtils):
            force(bool): to save even if it does exist
        """
        if key_mat == helper.file_mat:
            # NOT DONE, needed to save reference as single file with
            folder = helper.get_show_usd_location()
            ## use of the basename of the klf
            base_texture = ""
            material_json_dir = os.path.join(folder, constant.mat_subfolder)
            if len(material_list):
                DiskUtils.create_path_recursive(material_json_dir)
                for anode, data in material_list:
                    # get the filename from klf

                    kfile = anode.get_klf()
                    if kfile != "":
                        base_texture = os.path.basename(kfile).replace(
                            ".klf", constant.matfile_ext
                        )
                        material_json_file = os.path.join(
                            material_json_dir, base_texture
                        )
                        if not material_json_file in self.avoid_twice_mtl_export:
                            if not os.path.exists(material_json_file) or force == True:
                                with open(material_json_file, "w") as fout:
                                    fout.write(json.dumps(data, indent=4))
                        anode.set_data({constant.matfile: material_json_file})
                        self.avoid_twice_mtl_export.add(material_json_file)

        elif key_mat == constant.encoded:
            for anode, data in material_list:
                [
                    anode.set_data({constant.material: data})
                    for geom, data in material_list
                ]
        return True
