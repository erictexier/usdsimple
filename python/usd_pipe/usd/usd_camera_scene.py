# -*- coding: utf-8 -*-

import os
import re
from collections import defaultdict

# prx
from pxr import Kind, Sdf, Usd, UsdGeom, Gf

# DSK
from context_manager import Context

# local
from usd_pipe.usd.usdfile_utils import UsdFileUtils
from dsk.base.utils.disk_utils import DiskUtils


class UsdCameraScene(UsdFileUtils):
    """populate the assets models area with usd file:
    Create them all as variant of a geometry exported from abc
    """

    ShotFolder = "usdlayout"

    def __init__(self, ctx, outputdir, log):
        super(UsdCameraScene, self).__init__(ctx, outputdir, log)

    def build_usd_camera(self, nodelist, ascii=True, force=False):
        """"""

        asset_naming = dict()
        camera_path = self.get_show_usd_shot(UsdCameraScene.ShotFolder)
        convert_list = dict()
        for node in nodelist:
            abc_came = node.get_camera_abc()
            if not abc_came.endswith(".abc"):
                self.log.error("No supported  build_usd_camera{}".format(abc_came))
                continue
            filepathout = os.path.join(camera_path, "%s.usd" % node.name)
            DiskUtils.create_path_recursive(camera_path)
            convert_list[filepathout] = abc_came
            asset_naming[node.name] = filepathout

        if force == True:
            for dest in convert_list:
                src = convert_list[dest]
                # the initial _geom is built with a call to usdcat.
                self.create_asset_geom_from_abc(src, dest, ascii=ascii)
        else:
            for dest in convert_list:
                src = convert_list[dest]
                if not os.path.exists(dest):
                    # the initial _geom is built with a call to usdcat.
                    self.create_asset_geom_from_abc(src, dest, ascii=ascii)

        return asset_naming
