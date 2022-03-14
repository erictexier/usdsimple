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


class UsdScatterScene(UsdFileUtils):
    """populate the anim cache  with usd file:"""

    ShotFolder = "usdfx"
    AssetFolder = UsdFileUtils.ASSETS_SCATTER

    def __init__(self, ctx, outputdir, log):
        super(UsdScatterScene, self).__init__(ctx, outputdir, log)
        self._only_once = set([])

    def build_ptc_usd(self, anode, ascii=False, force=False):
        """"""
        assert anode.Property == "SCATTER_3D"
        asset_naming = dict()
        ptc_path = self.get_show_usd_shot(UsdScatterScene.ShotFolder)

        ptcfile = anode.get_ptc()
        if not ptcfile.endswith(".abc"):
            self.log.error(
                "No supported in  build_ptc_usd {}: {}".format(ptcfile, anode)
            )
            return asset_naming
        filepathout = os.path.join(ptc_path, "%s.usd" % anode.name)

        asset_naming[anode] = filepathout

        if filepathout in self._only_once:
            return asset_naming
        self._only_once.add(filepathout)

        if force == True:
            DiskUtils.create_path_recursive(ptc_path)
            self.create_asset_geom_from_abc(ptcfile, filepathout, ascii=ascii)
        else:
            if not os.path.exists(filepathout):
                DiskUtils.create_path_recursive(ptc_path)
                self.create_asset_geom_from_abc(ptcfile, filepathout, ascii=ascii)

        return asset_naming

    def build_asset_scatter(self, nodescat, ascii=False, force=False):
        """"""
        assert nodescat.Property == "SCAT_CACHE"
        asset_naming = dict()
        ptcfile = nodescat.get_ptc()

        if ptcfile is None:
            return asset_naming

        if not ptcfile.endswith(".abc"):
            self.log.error("No supported in build_asset_scatter{}".format(ptcfile))
            return asset_naming

        filename = os.path.splitext(os.path.basename(ptcfile))[0]

        ptc_path = self.get_show_usd_asset(UsdScatterScene.AssetFolder)

        anode = nodescat.anode_with_scatter
        instance = anode.get_geom_instance_data()

        if instance:
            subfolder = instance.vdestination.primname

        else:
            subfolder = UsdFileUtils.clean_asset_instance_number(anode.name)

        ptc_path = os.path.join(ptc_path, subfolder, instance.vdestination.version)

        if ascii:
            filepathout = os.path.join(ptc_path, "%s.usda" % filename)
        else:
            filepathout = os.path.join(ptc_path, "%s.usd" % filename)

        asset_naming[nodescat] = filepathout

        if filepathout in self._only_once:
            return asset_naming
        self._only_once.add(filepathout)

        if force == True:
            DiskUtils.create_path_recursive(ptc_path)
            self.create_asset_geom_from_abc(ptcfile, filepathout, ascii=ascii)
        else:
            if not os.path.exists(filepathout):
                DiskUtils.create_path_recursive(ptc_path)
                self.create_asset_geom_from_abc(ptcfile, filepathout, ascii=ascii)

        return asset_naming
