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


class UsdCrowdedScene(UsdFileUtils):
    """populate the anim cache + (mat ...) with usd file:"""

    ShotFolder = "usdcrowds"

    def __init__(self, ctx, outputdir, log):
        super(UsdCrowdedScene, self).__init__(ctx, outputdir, log)

    def build_usd_crowds(self, nodelist, ascii=False, force=False):
        """"""
        asset_naming = dict()
        convert_list = dict()
        for anode in nodelist:
            assert anode.Property == "GEOM_CROWD"

            anim_path = self.get_show_usd_shot(UsdCrowdedScene.ShotFolder)

            animfile = anode.get_animCache()
            if not animfile.endswith(".abc"):
                self.log.error("No supported in build_usd_crowds{}".format(animfile))
                continue
            name, field = anode.name.split(";")
            filepathout = os.path.join(anim_path, field, "%s.usd" % name)
            convert_list.update({filepathout: animfile})
            asset_naming[anode] = filepathout

        # convert all the abc
        if force == True:
            for dest in convert_list:
                src = convert_list[dest]
                self.create_asset_geom_from_abc(src, dest, ascii=ascii)
        else:
            for dest in convert_list:
                src = convert_list[dest]
                if not os.path.exists(dest):
                    self.create_asset_geom_from_abc(src, dest, ascii=ascii)

        return asset_naming
