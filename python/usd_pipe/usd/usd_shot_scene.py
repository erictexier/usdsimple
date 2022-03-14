# -*- coding: utf-8 -*-

import os

from collections import defaultdict

# prx
from pxr import Kind, Sdf, Usd, UsdGeom

# DSK
from context_manager import Context

# local
from usd_pipe.usd.usdfile_utils import UsdFileUtils
from dsk.base.utils.time_utils import StopWatch
from dsk.base.utils import shotgun_utils

from usd_pipe.usd.usd_camera_scene import UsdCameraScene
from usd_pipe.usd.usd_scatter_scene import UsdScatterScene
from usd_pipe.usd.usd_location_scene import UsdLocationScene
from usd_pipe.usd.usd_anim_scene import UsdAnimScene
from usd_pipe.usd.usd_crowded_scene import UsdCrowdedScene

from usd_pipe.api.dskscene_api import SchemaScene as Scene


class UsdShotScene(UsdFileUtils):
    """populate the assets models area with usd file:
    Create them all as variant of a geometry exported from abc
    """

    _scope = [
        "/World",
        "/World/geo",
        "/World/geo/camera",
        "/World/geo/set",
        "/World/geo/anim",
        "/World/geo/crowds",
        "/World/geo/scatters",
    ]
    world_camera = _scope[2]
    world_set = _scope[3]
    world_anim = _scope[4]
    world_crowds = _scope[5]
    world_scatters = _scope[6]

    # export are usd converted from abc
    # for now, the top node is always name 'all' which can be a choice later for usd export
    AllTag = "/all"
    CameraTag = "/shotCam"

    def __init__(self, ctx, outputdir, log):
        super(UsdShotScene, self).__init__(ctx, outputdir, log)

    def MakeShotStage(cls, path, ctx):

        stage = Usd.Stage.CreateNew(path)

        # pre -define layout
        scope = [UsdGeom.Scope.Define(stage, scope) for scope in cls._scope]
        stage.SetDefaultPrim(scope[0].GetPrim())
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

        shot_info = shotgun_utils.ShotgunUtils.shot_duration(ctx)
        stage.SetStartTimeCode(shot_info.sg_head_in)
        stage.SetEndTimeCode(shot_info.sg_tail_out)

        return stage

    @staticmethod
    def shot_list_relative(shot_name, ext):
        """ for reference, not used at the point

        Returns:
            dict(path): key as Scene label, value: relative location
        """
        return {
            Scene.fx: "./%s/%s_fx.%s" % (UsdScatterScene.ShotFolder, shot_name, ext),
            Scene.animation: "./%s/%s_anim.%s"
            % (UsdAnimScene.ShotFolder, shot_name, ext),
            Scene.crowds: "./%s/%s_crowds.%s"
            % (UsdCrowdedScene.ShotFolder, shot_name, ext),
            Scene.camera: "./%s/%s_camera.%s"
            % (UsdCameraScene.ShotFolder, shot_name, ext),
            Scene.layout: "./%s/%s_sets.%s"
            % (UsdLocationScene.AssetFolder, shot_name, ext),
        }

    def build_usd_shot(self, scene_naming, taskname=None, ascii=False, force=False):
        """
        Args:
            scene_naming(dict(list)): a some how, a list of keys value of type
                    of group (set, camera, animation etc...)
                    Depending on the type, the key can be xmlscene node or simple name.
                    the value is always a filename to reference
            taskname: a pointer to elaborate on diferente scene representation for different task
                      use for now to tag the shot_scene level of export-> all -> '', setanin etc...
            ascii(bool): save 'usda' of true else 'usd'
        """
        # top root directory. Important to not write outside the perimeter
        path_shot = self.get_show_usd_shot()
        self.CreateShotTask(
            self.ctx.shot, path_shot, scene_naming, taskname=taskname, ascii=ascii
        )

    def CreateShotTask(
        self, shot_name, shot_dir, scene_naming, taskname=None, ascii=False
    ):
        """
        Args:
            shot_name(str):
            shot_dir(str): shot folder to build the shotpath

        """
        SW = StopWatch()

        ext = "usda" if ascii else "usd"
        if len(scene_naming[Scene.crowds_label]) > 0:
            ext = "usd"
        if taskname is None or taskname.startswith("all"):
            shotpath = os.path.join(shot_dir, "%s.%s" % (shot_name, ext))
        else:
            shotpath = os.path.join(shot_dir, "%s_%s.%s" % (shot_name, taskname, ext))
        # local_folder = self.shot_list_relative(shot_name, ext)

        stage_shot = self.MakeShotStage(shotpath, self.ctx)

        SW1 = StopWatch()
        # load cameras
        self.camera_layers(stage_shot, scene_naming[Scene.camera_label])
        SW1.stop()
        self.log.info("Duration camera: {:.4f} seconds".format(SW1.elapsed()))

        SW1 = StopWatch()
        # load layout
        self.layout_layers(stage_shot, scene_naming[Scene.layout_label])
        SW1.stop()
        self.log.info("Duration layout: {:.2f} min".format(SW1.elapsed() / 60.0))

        SW1 = StopWatch()
        # load animation
        self.anim_layers(stage_shot, scene_naming[Scene.animation_label])
        SW1.stop()
        self.log.info("Duration anim: {:.2f} min".format(SW1.elapsed() / 60.0))

        SW1 = StopWatch()
        # load crowds
        self.crowds_layers(stage_shot, scene_naming[Scene.crowds_label])
        SW1.stop()
        self.log.info("Duration crowds: {:.2f} min".format(SW1.elapsed() / 60.0))

        for scatter in scene_naming[Scene.scatterasset_label][:4]:
            node, path = scatter.items()[0]
            print(node.anode_with_scatter.name, path)

        for scatter in scene_naming[Scene.scattershot_label]:
            node, path = scatter.items()[0]
            print(node.name, path)

        SW1 = StopWatch()
        # save
        stage_shot.Save()
        SW1.stop()
        self.log.info(
            "Duration saving shot: {} : {:.2f} min".format(
                shotpath, SW1.elapsed() / 60.0
            )
        )
        SW.stop()
        self.log.info("Done: {:.3f} min".format(SW.elapsed() / 60.0))

    def camera_layers(self, stage, camera_nodes, label=""):
        """ if label != "" use it to get reference as relative path(see wrongly done for now)
        """
        # tell which layer to word on

        for camera_node in camera_nodes:
            for camera_name in camera_node:
                # keys are name of the camera
                camera_layer_path = camera_node[camera_name]
                camera = UsdGeom.Xform.Define(stage, self.world_camera)
                camera_top = UsdGeom.Camera.Define(
                    stage, "%s/%s" % (self.world_camera, camera_name)
                )
                camera_top.GetPrim().GetReferences().AddReference(
                    assetPath=camera_layer_path, primPath=self.CameraTag
                )

    def layout_layers(self, stage, layout_nodes, label=""):
        """ if label != "" use it to get reference as relative path(see wrongly done for now)
        """
        for layout_node in layout_nodes:
            for layout_name in layout_node:
                print(layout_name)
                # keys are name
                layout_layer_path = layout_node[layout_name]
                layout = UsdGeom.Xform.Define(stage, self.world_set)
                layout_top = UsdGeom.Xform.Define(
                    stage, "%s/%s" % (self.world_set, layout_name)
                )
                layout_top.GetPrim().GetReferences().AddReference(
                    assetPath=layout_layer_path, primPath="/%s" % layout_name
                )

    def anim_layers(self, stage, anim_nodes, label=""):
        """ if label != "" use it to get reference as relative path(see wrongly done for now)
        """
        for anim_node in anim_nodes:
            for an_anim in anim_node:
                # keys are scenexml
                anim_name = an_anim.name
                if (
                    "eptMagicFactoryExtB_base" in anim_name
                    or "eptFoodTruckD_base" in anim_name
                ):
                    # this is geom with issue: To Do
                    continue
                anim_layer_path = anim_node[an_anim]
                anim = UsdGeom.Xform.Define(stage, self.world_anim)
                anim_top = UsdGeom.Xform.Define(
                    stage, "%s/%s" % (self.world_anim, anim_name)
                )
                anim_top.GetPrim().GetReferences().AddReference(
                    assetPath=anim_layer_path, primPath=self.AllTag
                )

    def crowds_layers(self, stage, crowds_nodes, label=""):
        """ if label != "" use it to get reference as relative path(see wrongly done for now)
        """
        for crowds_node in crowds_nodes:
            for an_crowds in crowds_node:
                # keys are scenexml
                crowds_name = an_crowds.name
                local_name, crowds_field = crowds_name.split(";")
                crowds_layer_path = crowds_node[an_crowds]
                crowds = UsdGeom.Xform.Define(stage, self.world_crowds)

                crowds_top = UsdGeom.Xform.Define(
                    stage, "%s/%s/%s" % (self.world_crowds, crowds_field, local_name)
                )
                crowds_top.GetPrim().GetReferences().AddReference(
                    assetPath=crowds_layer_path, primPath=self.AllTag
                )
