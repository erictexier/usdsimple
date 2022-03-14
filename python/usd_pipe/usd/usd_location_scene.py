# -*- coding: utf-8 -*-

import os
import math
from collections import defaultdict

# pxr
from pxr import Kind, Sdf, Usd, UsdGeom, Gf


# DSK
from context_manager import Context

# local
from usd_pipe.usd.usdfile_utils import UsdFileUtils
from usd_pipe.usd.usd_model_scene import UsdModelScene
from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.time_utils import StopWatch

from usd_pipe.io.scenexml import InstanceScatCache


class TransformMtxUsb(object):
    """ Build a base transformation for usd base on XmlScene
    Should be move to utils. needs testing to see if it's the right order of transform.
    """

    _pi = math.acos(0) * 2

    @classmethod
    def set_transform(cls, to_work_on, nodegeom):

        transform = nodegeom.get_xform()
        xform = [float(x) for x in transform.split(" ")]

        translate = xform[12:-1]
        try:
            angle = math.asin(xform[8]) * 180.0 / cls._pi
        except:
            angle = 0
        scale = xform[5]
        # print("info mtx", translate, angle, scale)

        UsdGeom.XformCommonAPI(to_work_on).SetXformVectors(
            translation=Gf.Vec3d(translate),
            rotation=Gf.Vec3f(0.0, angle, 0.0),
            scale=Gf.Vec3f(scale, scale, scale),
            pivot=Gf.Vec3f(0.0, 0.0, 0.0),
            rotationOrder=UsdGeom.XformCommonAPI.RotationOrderXYZ,  # RotationOrderYXZ
            time=Usd.TimeCode.Default(),
        )


class UsdLocationScene(UsdFileUtils):
    """populate the assets models area with usd file:
    Create them all as variant of a geometry exported from abc
    """

    AssetFolder = UsdFileUtils.ASSETS_LOCATION

    def __init__(self, ctx, outputdir, log):
        super(UsdLocationScene, self).__init__(ctx, outputdir, log)

    def get_scatter_in_locations(self, anode):
        """ This method is to externalize the scatter asset to region, even 
        if we don't save location because the location file exists
        Note: This consider the set to be a frozen node for now.
        """
        subregion = anode.get_delegate()
        dup = defaultdict(list)
        for sub in subregion:
            locnode = subregion[sub]
            prim_name_sub = locnode.name
            dup[prim_name_sub].append(locnode)
        sub_loc = {}
        for subkey in dup:
            for locnode in dup[subkey]:
                for nodegeom in locnode.get_asset_list():
                    if nodegeom.Property != "REGION_3D":
                        scat = nodegeom.get_scatter_abc()
                        if scat not in [None, ""]:
                            newnode = InstanceScatCache()
                            newnode.set_node_scatter(nodegeom, [anode, locnode])
                    else:
                        # inside a loc
                        for inside_loc in nodegeom.get_asset_list():
                            if scat not in [None, ""]:
                                newnode = InstanceScatCache()
                                newnode.set_node_scatter(
                                    nodegeom, [anode, locnode, inside_loc]
                                )

    def build_usb_location_asset(self, anode, ascii=True, force=False):
        """ Things like Set And Foliages As Assets
        Args:
            nodelist(list): list of instance (anim, model ....)
            force(bool): if True and file exists, update
        Returns:
            dict():  key: instance name
                     value: the usb set path
        """
        SW = StopWatch()
        SW1 = StopWatch()

        asset_naming = dict()

        # create a model path under model/location
        asset_path = self.get_show_usd_asset(UsdLocationScene.AssetFolder)
        if self.ctx.shot is not None:
            asset_path = os.path.join(asset_path, self.ctx.shot)
        elif self.ctx.sequence is not None:
            asset_path = os.path.join(asset_path, self.ctx.sequence)
        else:
            self.info.error("Not support at project level: {}".format(self.ctx.project))
            return dict()

        self.log.info("USD asset location {}".format(anode.name))

        # first build subregion as prim
        subregion = anode.get_delegate()

        sub_location_list = list()

        # address duplicate name in subregion
        dup = defaultdict(list)
        for sub in subregion:
            locnode = subregion[sub]
            prim_name_sub = locnode.name
            dup[prim_name_sub].append(locnode)

        sub_loc = {}
        for subkey in dup:
            if len(dup[subkey]) > 1:
                # index the sub_region with _%d
                for index, sub in enumerate(dup[subkey]):
                    # with index sublocation to be unique
                    sub_loc[subkey + "_%d" % index] = sub
            else:
                sub_loc[subkey] = dup[subkey][0]

        SW1.stop()
        self.log.info("Duration prep: {:.2f} minutes".format(SW1.elapsed() / 60.0))
        SW1 = StopWatch()

        for index, sub in enumerate(sub_loc):
            locnode = sub_loc[sub]
            prim_name_sub = locnode.name

            stage_location = os.path.join(
                asset_path, prim_name_sub, "%s_%d.usda" % (prim_name_sub, index)
            )
            prim_name_sub = "%s_%d" % (prim_name_sub, index)
            if not os.path.exists(stage_location) or force == True:
                stage_region = Usd.Stage.CreateNew(stage_location)
                setSubRegionPrim = UsdGeom.Xform.Define(
                    stage_region, "/%s" % prim_name_sub
                ).GetPrim()
                stage_region.SetDefaultPrim(setSubRegionPrim)

                Usd.ModelAPI(setSubRegionPrim).SetKind(Kind.Tokens.assembly)

                for nodegeom in locnode.get_asset_list():
                    if "eptCinemaTheatreExt_base" in anode.name:
                        print anode.get_geom_instance_data
                    # for now: with lookup with variant versioned, the issue is to
                    # be sure that there is no name conflict
                    if nodegeom.Property != "REGION_3D":
                        # scatter are handle outside location with location xform
                        scat = nodegeom.get_scatter_abc()
                        if scat not in [None, ""]:
                            continue
                        try:
                            # discard scatter
                            self._AddAsset(stage_region, prim_name_sub, nodegeom)
                        except Exception as e:
                            self.log.error(
                                "{}: naming shot be check on properties: {}".format(
                                    nodegeom.Property, e
                                )
                            )
                    else:
                        for inside_loc in nodegeom.get_asset_list():
                            scat = inside_loc.get_scatter_abc()
                            if scat not in [None, ""]:
                                # scatter are handle outside location with location xform
                                continue
                            try:
                                self._AddAsset(stage_region, prim_name_sub, inside_loc)
                            except Exception as e:
                                self.log.error(
                                    "{}: naming shot be check on properties: {}".format(
                                        inside_loc.Property, e
                                    )
                                )
                # saving sub region
                stage_region.GetRootLayer().Save()

            sub_location_list.append([prim_name_sub, stage_location, locnode])

        SW1.stop()
        self.log.info(
            "Duration Sublocation to .usb: {:.2f} minutes".format(SW1.elapsed() / 60.0)
        )
        SW1 = StopWatch()

        # build a SET with containing sub region
        prim_name = anode.name
        region_path = os.path.join(asset_path, prim_name, "%s.usda" % prim_name)
        asset_naming[anode.name] = region_path
        if not os.path.exists(region_path) or force == True:
            stage = Usd.Stage.CreateNew(region_path)
            setModelPrim = UsdGeom.Xform.Define(stage, "/%s" % prim_name).GetPrim()
            stage.SetDefaultPrim(setModelPrim)
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
            Usd.ModelAPI(setModelPrim).SetKind(Kind.Tokens.assembly)
            for sub in sub_location_list:
                subref = self._AddModelRef(
                    stage, "/%s/%s" % (prim_name, sub[0]), sub[1]
                )
                locnode = sub[2]
                xform = locnode.get_transform_api()
                TransformMtxUsb.set_transform(subref, xform)
            stage.GetRootLayer().Save()
        SW1.stop()
        self.log.info(
            "Duration Main Location: {:.2f} minutes".format(SW1.elapsed() / 60.0)
        )
        SW.stop()
        self.log.info(
            "Duration model layout: {:.2f} minutes".format(SW.elapsed() / 60.0)
        )
        return asset_naming

    def _AddAsset(self, stage, prim_name, nodegeom):
        asset_path = ""
        to_work_on = None

        instance = nodegeom.get_geom_instance_data()
        if instance:
            asset_path = os.path.join(
                instance.vdestination.folder, instance.vdestination.variant_fname
            )
            if asset_path and os.path.exists(asset_path):
                to_work_on = self._AddModelRef(
                    stage,
                    "/%s/%s" % (prim_name, instance.vdestination.primname),
                    asset_path,
                )
        else:
            self.log.error("Trouble: not properly named: {}".format(nodegeom.name))

        if to_work_on is None:
            return None

        TransformMtxUsb.set_transform(to_work_on, nodegeom)

        # we conveniently named the shadingVariant the same as the name of
        # the ball.
        shadingVariantName = to_work_on.GetName()

        # get the variantSet "shadingVariant" and then set it accordingly.
        vs = to_work_on.GetVariantSets().GetVariantSet("shadingVariant")
        vs.SetVariantSelection(shadingVariantName)
        return to_work_on

    def _AddModelRef(self, stage, path, refPath):
        """
        Adds a reference to refPath at the given path in the stage.  This will make
        sure the model hierarchy is maintained by ensuring that all ancestors of
        the path have "kind" set to "group".

        returns the referenced model.
        """

        from pxr import Kind, Sdf, Usd, UsdGeom

        # convert path to an Sdf.Path which has several methods that are useful
        # when working with paths.  We use GetPrefixes() here which returns a list
        # of all the prim prefixes for a given path.
        path = Sdf.Path(path)
        # print path
        # print path.GetPrefixes()
        for prefixPath in path.GetPrefixes()[1:-1]:
            parentPrim = stage.GetPrimAtPath(prefixPath)
            if not parentPrim:
                parentPrim = UsdGeom.Xform.Define(stage, prefixPath).GetPrim()
                Usd.ModelAPI(parentPrim).SetKind(Kind.Tokens.group)

        # typeless def here because we'll be getting the type from the prim that
        # we're referencing.
        m = stage.DefinePrim(path)
        m.GetReferences().AddReference(refPath)
        return m

