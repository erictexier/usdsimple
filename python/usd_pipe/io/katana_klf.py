# -*- coding: utf-8 -*-

import sys
import os
import re
import datetime
from collections import defaultdict
import json

# DSK
import logging
from config_manager import ConfigManager


logger = logging.getLogging(__name__)


# setup the scenegraph for example
from usd_pipe.io.scenexml import SceneXml

# for to instance Arbitrary list (container)
# schema
from usd_pipe.io.scenexml import constant as scncst
from usd_pipe.api.dskscene_api import SchemaScene as Scene
from usd_pipe.io.xml_scene_io import XmlSceneIO

# class top node of an scene graph xml description
from usd_pipe.io.scenexml import ScenegraphXml

# geom node
from usd_pipe.io.scenexml import InstanceAnimSceneXml as AnimScene
from usd_pipe.io.scenexml import InstanceCrowdsSceneXml as CrowdsScene
from usd_pipe.io.scenexml import InstanceScatterSceneXml as ScatterScene
from usd_pipe.io.scenexml import InstanceCameraSceneXml as CameraScene
from usd_pipe.io.scenebams import SceneBams

# manage file naming to help
from usd_pipe.usd.usdfile_utils import UsdFileUtils

# bams support for scene
from usd_pipe.api import dskscene_api

# init the log
SceneXml.set_log(None)


from usd_pipe.api.dskscene_api import SceneBuilder


class KatanaKlf(SceneBuilder):
    @classmethod
    def katana_scan(cls, in_scene):
        """
        Args:
            in_scene(str): a scene from katana, livegroup
        Returns:
            defaultdict(list): key: layout, camera ..., list of scene element
        """
        # local katana depend
        from usd_pipe.io.katana_utils.scanner import Scanner

        result = defaultdict(list)

        KatanaFile.Load(in_scene)
        # IN QUESTION: if we want that all node query are properly initialised
        # it only query node in in shot Input and after loading klf

        # ensure that all macros are loaded before we begin the eval
        PyUtilModule.UserNodes.ReloadCustomNodes()

        # for time eval example ?
        # nodes = cat[cls.AnimationLoader]
        # for node in nodes:
        #     pnode = Nodes3DAPI.GetGeometryProducer(node, graphState=1000)

        # simple scanning of input
        # classify all node by types:
        nodes = NodegraphAPI.GetAllNodes()
        cat = defaultdict(list)
        for node in nodes:
            if node.isMarkedForDeletion() or node.isBypassed():
                continue
            parent = node.getParent()
            if parent and parent.getName() == "SHOT_INPUT":
                cat[node.getType()].append(node)
            elif node.getType() == "Render":
                # just in case
                cat[node.getType()].append(node)

        # CAMERA
        nodes = cat[Scanner.CameraLoader]
        assert len(nodes) == 1
        # deal with multiple camera later
        for node in nodes:
            node_name = node.getName().replace("_loader", "")
            data = Scanner.scan_camera(node)
            if scncst.cameraabc in data:
                if os.path.exists(data[scncst.cameraabc]):
                    data.update({"name": node_name})
                    cam = CameraScene()
                    cam.set_data(data)
                    result[Scene.camera].append(cam)

        # LAYOUT
        nodes = cat[Scanner.LayoutLoader]
        for node in nodes:
            node_name = node.getName().replace("_loader", "")
            for ch in node.getChildren():
                if ch.getType() == "ScenegraphXml_In":
                    scenefile = Scanner.scan_layout_scene(ch)
                    if scenefile and os.path.exists(scenefile):
                        res = cls.scenegraph_scan(scenefile)
                        # a dict here, not a node
                        result[Scene.layout].append(res)

        ## SCATTER
        nodes = cat["Group"]
        for node in nodes:
            if Scene.scatter in node.getName():
                node_name = node.getName().replace("_loader", "")
                node_name = node_name.replace("_scatter", "")
                tmpresult = Scanner.scan_scatter(node)
                if scncst.abcscatter in tmpresult:
                    if os.path.exists(tmpresult[scncst.abcscatter]):
                        asset_list = UsdFileUtils.get_asset_scatter(
                            tmpresult[scncst.abcscatter]
                        )
                        if asset_list:
                            tmpresult.update(
                                {scncst.assetscatter: ";".join(asset_list)}
                            )
                        tmpresult.update({"name": node_name})
                        obj = ScatterScene()
                        obj.set_data(tmpresult)
                        result[Scene.scatter].append(obj)

        # ANIMATION
        nodes = cat[Scanner.AnimationLoader]
        for node in nodes:
            node_name = node.getName().replace("_loader", "")
            obj = AnimScene()
            tmpresult = Scanner.scan_animated(node)
            tmpresult.update({"name": node_name})
            obj.set_data(tmpresult)
            result[Scene.animation].append(obj)

        # CROWDS
        nodes = cat[Scanner.CrowdLoader]
        for node in nodes:
            node_name = node.getName()
            m = cls._pat_crowd.search(node_name)
            if m:
                node_name = node_name.replace(
                    m.group(), "{}{}".format(cls._crowd_sep, m.group()[1:-7])
                )
            else:
                node_name = node_name.replace("_loader", "")
            obj = CrowdsScene()
            tmpresult = Scanner.scan_animated(node)
            tmpresult.update({"name": node_name})
            obj.set_data(tmpresult)
            result[Scene.crowds].append(obj)

        return result

    def load_and_process(self, ctx, in_scene, material, outdir, force):
        """load shot, extract all files and material references
        in progress
        This section need to be evaluated at frame range (maybe)
        Args:
            in_scene(str): a scene from katana, livegroup, json or xml
            material(string): see usdfile_utils.UsdFileUtils.scene_type_mat
        """
        # local katana depend
        from usd_pipe.io.katana_utils.scanner import Scanner

        super(KatanaKlf, self).load_and_process(
            ctx, in_scene, material, outdir, Scanner, force
        )

        return True


def get_context(short_path):
    from context_manager import Context

    ctx = (
        Context.from_short_path(short_path, validate=True)
        if short_path is not None
        else Context.from_environment(validate=True)
    )
    return ctx


if __name__ == "__main__":

    # To insure alembic lib are used
    from Katana import KatanaFile, NodegraphAPI
    import PyUtilModule
    from alembic_tools import cask, util
    import alembic_tools

    shot_path = sys.argv[1]
    in_scene = sys.argv[2]
    material = sys.argv[3]
    outdir = sys.argv[4]
    force = True if sys.argv[5] == "1" else False
    assert len(sys.argv) == 6

    # check argument
    assert material in UsdFileUtils.scene_type_mat
    ctx = get_context(shot_path)
    logger.info("****Processing %s\n****" % in_scene)
    # to allow for query in bams for scenegraph
    ScenegraphXml.set_bams(SceneBams(ctx))
    proce = KatanaKlf()
    proce.load_and_process(ctx, in_scene, material, outdir, force)
