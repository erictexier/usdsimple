# -*- coding: utf-8 -*-

import os

from collections import defaultdict

# prx
from pxr import Kind, Sdf, Usd, UsdGeom, Gf

# DSK
from context_manager import Context

# local
from usd_pipe.usd.usdfile_utils import UsdFileUtils
from dsk.base.utils.disk_utils import DiskUtils

from usd_pipe.io.scenexml import constant as scncst


class UsdAnimScene(UsdFileUtils):
    """populate the anim cache  with usd file:"""

    ShotFolder = "usdanim"

    def __init__(self, ctx, outputdir, log):
        super(UsdAnimScene, self).__init__(ctx, outputdir, log)

    def build_usd_anim(self, nodelist, ascii=True, force=False):
        """"""
        asset_naming = dict()
        convert_list = dict()
        for anode in nodelist:
            assert anode.Property == "GEOM_ANIM_3D"

            anim_path = self.get_show_usd_shot(UsdAnimScene.ShotFolder)

            animfile = anode.get_animCache()
            if not animfile.endswith(".abc"):
                self.log.error("No supported in build_usd_anim: {}".format(animfile))
                continue
            filepathout = os.path.join(anim_path, "%s.usd" % anode.name)
            convert_list.update({filepathout: animfile})
            asset_naming[anode] = filepathout

        # convert all the abc
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
