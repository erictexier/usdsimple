# -*- coding: utf-8 -*-
import os

from collections import defaultdict

# local
from usd_pipe.io import xml_scene_io
from usd_pipe.io import scenexml
from usd_pipe.io.scenexml import SceneXml

# for to instance Arbitrary list (container)
from usd_pipe.io.scenexml import constant as scncst
from usd_pipe.io.xml_scene_io import XmlSceneIO
from usd_pipe.api.dskscene_api import SchemaScene as Scene

from usd_pipe.io.scenexml import ScenegraphXml
from usd_pipe.io.scenexml import InstanceAnimSceneXml as AnimScene
from usd_pipe.io.scenexml import InstanceCrowdsSceneXml as CrowdsScene
from usd_pipe.io.scenexml import InstanceScatterSceneXml as ScatterScene
from usd_pipe.io.scenexml import InstanceCameraSceneXml as CameraScene
from usd_pipe.usd.usdfile_utils import UsdFileUtils

# it's a debug statement to build smaller test:
#  NO_LAYOUT:  everything but LAYOUT
#  ONLY_LAYOUT: everything but ANIMATIONS AND CROWDED
#  Default: NO_LAYOUT = False, ONLY_LAYOUT = False
NO_LAYOUT = False
ONLY_LAYOUT = False


class ManifestJsonXml(object):
    __only_key = [
        Scene.layout,
        Scene.scatter,
        Scene.camera,
        Scene.grass,
        Scene.crowds,
        Scene.animation,
        Scene.fx,
    ]

    @staticmethod
    def pop_key(key, data_all):
        if key in data_all:
            assert key in ManifestJsonXml.__only_key
            data = data_all.pop(key)
            return data
        return None

    @classmethod
    def scene_from_json(cls, json_file):

        data_all = xml_scene_io.XmlSceneIO.read_from_json(json_file)
        narrowed = dict()
        for key in data_all.keys():
            narrowed[key] = cls.pop_key(key, data_all)

        master = UsdFileUtils.get_scene_header_node("from_json", UsdFileUtils.no_mat)
        container_world = SceneXml(
            scncst.attrlist
        )  # should be a list or directly master child
        container_world.name = "World"
        master.add_child(container_world)

        result = defaultdict(list)
        for key in narrowed:
            if key == Scene.layout:
                if NO_LAYOUT:
                    continue
                for node_name in narrowed[key]:
                    for subdict in narrowed[key][node_name]:
                        scene_file = narrowed[key][node_name][subdict]
                        if scene_file and os.path.exists(scene_file):
                            all_class_name = SceneXml.factory([], None)
                            all_class_name.update(scenexml._Generator)
                            node_scene = XmlSceneIO.read_scene(
                                scene_file, all_class_name
                            )
                            node_scene.update_subregion()
                            result[Scene.layout].append(
                                {
                                    Scene.token_label: node_name,
                                    Scene.scenegraph_label: scene_file,
                                    Scene.topnode_label: node_scene,
                                }
                            )
            elif key == Scene.camera:
                for node_name in narrowed[key]:
                    for subdict in narrowed[key][node_name]:
                        camera_scene = narrowed[key][node_name][subdict]
                        if camera_scene and os.path.exists(camera_scene):
                            cam = CameraScene()
                            data = {"name": node_name, scncst.cameraabc: camera_scene}
                            cam.set_data(data)
                            result[Scene.camera].append(cam)

            elif key in [Scene.scatter, Scene.grass, Scene.fx]:
                for node_name in narrowed[key]:
                    for subdict in narrowed[key][node_name]:
                        scatter_file = narrowed[key][node_name][subdict]
                        if scatter_file and os.path.exists(scatter_file):
                            data = {"name": node_name, scncst.abcscatter: scatter_file}
                            try:
                                asset_list = UsdFileUtils.get_asset_scatter(
                                    scatter_file
                                )
                                if asset_list:
                                    data.update(
                                        {scncst.assetscatter: ";".join(asset_list)}
                                    )
                            except:
                                print(
                                    "ManifestJsonXml: NEEDS TO BE FIXED: DOESN'T work in katana env: wrong plugs"
                                )
                            obj = ScatterScene()
                            obj.set_data(data)
                            result[Scene.scatter].append(obj)

            elif key == Scene.crowds:
                if ONLY_LAYOUT:
                    continue
                for node_name in narrowed[key]:
                    data = narrowed[key][node_name]
                    if "material" in data:
                        mat = data.pop("material")
                        data.update({scncst.lookfile: mat})
                    if "model" in data:
                        mat = data.pop("model")
                        data.update({scncst.modelfile: mat})
                    data.update({"name": node_name})
                    crowd = CrowdsScene()
                    crowd.set_data(data)
                    result[Scene.crowds].append(crowd)

            elif key == Scene.animation:
                if ONLY_LAYOUT:
                    continue
                for node_name in narrowed[key]:
                    data = narrowed[key][node_name]
                    data.update({"name": node_name})
                    if "material" in data:
                        mat = data.pop("material")
                        data.update({scncst.lookfile: mat})
                    if "model" in data:
                        mat = data.pop("model")
                        data.update({scncst.modelfile: mat})
                    anim = AnimScene()
                    anim.set_data(data)
                    result[Scene.animation].append(anim)
            else:
                raise Exception("not supported {}".format(key))
        return result

    @classmethod
    def get_main_files_manifest(cls, json_file):

        narrowed = xml_scene_io.XmlSceneIO.read_from_json(json_file)
        result = defaultdict(list)
        if Scene.layout in narrowed:
            layout = narrowed.pop(Scene.layout)
            for xx in layout:
                result[Scene.layout].append({xx: layout[xx]})
        if Scene.camera in narrowed:
            camera = narrowed.pop(Scene.camera)
            for xx in camera:
                result[Scene.camera].append({xx: camera[xx]})
        if Scene.scatter in narrowed:
            scatter = narrowed.pop(Scene.scatter)
            for xx in scatter:
                result[Scene.scatter].append({xx: scatter[xx]})
        if Scene.grass in narrowed:
            grass = narrowed.pop(Scene.grass)
            for xx in grass:
                result[Scene.grass].append({xx: grass[xx]})
        if Scene.fx in narrowed:
            fx = narrowed.pop(Scene.fx)
            for xx in fx:
                result[Scene.fx].append({xx: fx[xx]})
        return result
