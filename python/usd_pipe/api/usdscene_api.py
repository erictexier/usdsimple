# -*- coding: utf-8 -*-

from collections import defaultdict


from usd_pipe.usd.usd_model_scene import UsdModelScene
from usd_pipe.usd.usd_location_scene import UsdLocationScene
from usd_pipe.usd.usd_camera_scene import UsdCameraScene
from usd_pipe.usd.usd_anim_scene import UsdAnimScene
from usd_pipe.usd.usd_crowded_scene import UsdCrowdedScene
from usd_pipe.usd.usd_scatter_scene import UsdScatterScene
from usd_pipe.usd import usdfile_utils
from usd_pipe.api.dskscene_api import SchemaScene as shem_s


class UsdSceneApi(usdfile_utils.UsdFileUtils):
    def __init__(self, ctx, outputdir, log):
        super(UsdSceneApi, self).__init__(ctx, outputdir, log)
        self.scene_desc = None

    def get_scene(self, via):
        self.scene_desc = super(UsdSceneApi, self).get_scene(via)
        return self.scene_desc

    @property
    def description(self):
        return self.scene_desc

    def model_export_usd(
        self, do_model=True, do_anim=False, do_crowd=False, force=False,
    ):
        """ Since animation and crowds use directly their animcache at this point they are not requiered
        to have asset usd checked. It will be needed when we do rig non cached


        Returns:
            defaultdict(list): only scatter needs to be tag
        """
        usdf_model = UsdModelScene(self.ctx, self.get_outdir(), self.log)

        if do_model:
            self.build_assets_model(usdf_model, self.scene_desc, "GEOM_3D", force)
        if do_anim:
            self.build_assets_model(usdf_model, self.scene_desc, "GEOM_ANIM_3D", force)
        if do_crowd:
            self.build_assets_model(usdf_model, self.scene_desc, "GEOM_CROWD", force)

    def export_assets_common(
        self, via, list_of_gate_keeper, do_anim=False, do_crowd=False, force=False
    ):
        scene_desc = self.get_scene(via)
        scene_list = [scene_desc]
        for gk in list_of_gate_keeper:
            usdapi = UsdSceneApi(gk.ctx, self.get_outdir(), self.log)
            scene_extra = usdapi.get_scene(via)
            assert scene_extra
            scene_list.append(usdapi)

        objectlist = list()
        for sceneapi in scene_list:
            scene = sceneapi.scene_desc
            objectlist.extend(scene.get_register()["GEOM_3D"])
            if do_anim:
                objectlist.extend(scene.get_register()["GEOM_ANIM_3D"])
            if do_crowd:
                objectlist.extend(scene.get_register()["GEOM_CROWD"])

        usdf_model = UsdModelScene(self.ctx, self.get_outdir(), self.log)
        # build all the asset in one list to avoid exporting twice (as the same
        # asset can be instanciate from multiple shot)
        self.build_assets_model_shared(usdf_model, objectlist, force)
        return scene_list

    def export_shot_simple(
        self,
        asset_done=False,
        do_region=False,
        do_asset_scatter=False,
        do_anim=False,
        do_crowd=False,
        do_shot_scatter=False,
        do_all=False,
        force=False,
    ):
        """ This straight export: anim are animCache, simCache of set... 
        no rig so we don't need the model asset of those
        """
        assert self.scene_desc is not None
        scene_naming = defaultdict(list)

        if asset_done == False:
            self.model_export_usd(
                do_model=True,
                do_anim=True if do_all else False,
                do_crowd=True if do_all else False,
                force=force,
            )
            if do_region:
                scene_naming[shem_s.layout_label] = self.export_location_usd(force)

        elif do_region:
            # export the ptc
            scene_naming[shem_s.layout_label] = self.export_location_usd(force)

        if do_asset_scatter:
            # only scatter needs to be tag
            scene_naming[shem_s.scatterasset_label] = self.export_scatter_from_location(
                force
            )

        # always export the shot camera if found
        scene_naming[shem_s.camera_label] = self.export_camCache(force)

        if do_anim:
            scene_naming[shem_s.animation_label] = self.export_animCache(force)

        if do_crowd:
            scene_naming[shem_s.crowds_label] = self.export_crowdSimCache(force)

        if do_shot_scatter:
            scene_naming[shem_s.scattershot_label] = self.export_scatter(force)
        return scene_naming

    def export_location_usd(self, force):
        assert self.scene_desc is not None
        result = list()
        locationusd = UsdLocationScene(self.ctx, self.get_outdir(), self.log)
        geomlist = self.scene_desc.get_register()["REGION_3D"]
        for loc in geomlist:
            res = locationusd.build_usd_location_asset(loc, force=force)
            result.append(res)
        return result

    def export_scatter_from_location(self, force):
        """ Location have certain asset that come from ptc, here with just locate
        them as SCAT_CACHE ( they are not part of the location_exported)

        Returns:
            (list) see: UsdScatterScene.build_asset_scatter
        """
        self.log.info("export_scatter_from_location")
        assert self.scene_desc is not None
        result = list()
        locationusd = UsdLocationScene(self.ctx, self.get_outdir(), self.log)
        geomlist = self.scene_desc.get_register()["REGION_3D"]
        for loc in geomlist:
            # to push scatter in location to ScatCache
            locationusd.get_scatter_from_locations(loc)

        # the location_uds register, can happen only after location
        ascatslist = self.scene_desc.get_register()["SCAT_CACHE"]
        usdf_model = UsdModelScene(self.ctx, self.get_outdir(), self.log)
        usdf_model.build_usd_model_asset([x.anode_with_scatter for x in ascatslist])
        # for asset create with ptc and instanciate in location
        for scatter_ptc in ascatslist:
            ptc = UsdScatterScene(self.ctx, self.get_outdir(), self.log)
            res = ptc.build_asset_scatter(scatter_ptc, force=force, ascii=False)
            if res:
                result.append(res)
        return result

    def export_scatter(self, force):
        """ for asset scatter, export subasset as model first then the ptc

        Returns:
            (list): see UsdScatterScene.build_ptc_usd
        """
        assert self.scene_desc is not None
        self.log.info("In export scatter")
        result = list()
        scatters = self.scene_desc.get_register()["SCATTER_3D"]
        usdf_model = UsdModelScene(self.ctx, self.get_outdir(), self.log)
        for scatter_ptc in scatters:
            usdf_model.build_usd_model_asset(scatter_ptc.get_subasset_list())
            ptc = UsdScatterScene(self.ctx, self.get_outdir(), self.log)
            res = ptc.build_ptc_usd(scatter_ptc, force=force, ascii=False)
            if res:
                result.append(res)
        return result

    def export_camCache(self, force):
        """
        Returns:
            (list): see build_usd_camera
        """
        assert self.scene_desc is not None
        result = list()
        camera_cache = UsdCameraScene(self.ctx, self.get_outdir(), self.log)
        geomlist = self.scene_desc.get_register()["CAMERA"]
        res = camera_cache.build_usd_camera(geomlist)
        if res:
            result.append(res)
        return result

    def export_animCache(self, force):
        """ AnimCache
            we can probably connect with model asset data by reference
        Returns:
            (list): see build_usd_anim
        """
        assert self.scene_desc is not None
        result = list()
        geomlist = self.scene_desc.get_register()["GEOM_ANIM_3D"]
        anim_char = UsdAnimScene(self.ctx, self.get_outdir(), self.log)
        res = anim_char.build_usd_anim(geomlist, force=force)
        if res:
            result.append(res)
        return result

    def export_crowdSimCache(self, force):
        """
        Returns:
            (list): see build_usd_crowds
        """
        assert self.scene_desc is not None
        result = list()
        # AnimSimCache
        geomlist = self.scene_desc.get_register()["GEOM_CROWD"]
        crowd_char = UsdCrowdedScene(self.ctx, self.get_outdir(), self.log)
        res = crowd_char.build_usd_crowds(geomlist)
        if res:
            result.append(res)
        return result

    @staticmethod
    def build_assets_model(usdf_model, scene_desc, tag, force):
        """ all geom found get exported as asset model

        Args:
            usdf_model(UsdModelScene): helper to build_usd_model_asset
            tag: in GEOM_3D, GEOM_ANIM_3D, GEOM_CROWD
        """
        assert scene_desc is not None
        result = dict()
        assert isinstance(usdf_model, UsdModelScene)
        registered = scene_desc.get_register()
        if tag in registered:
            geomlist = scene_desc.get_register()[tag]
            usdf_model.log.info("found: {}".format(len(geomlist)))
            result = usdf_model.build_usd_model_asset(geomlist, force=force)
            usdf_model.log.info("process model: {}".format(len(result)))
        return result

    @staticmethod
    def build_assets_model_shared(usdf_model, geomlist, force):
        """ all geom found get exported as asset model comming. 
            Similar to build_assets_model for many shots: force to true will
            make the process more efficient.
        Args:
            usdf_model(UsdModelScene): helper to build_usd_model_asset
            geomlist: list of asset node
        """
        assert nodelist is not None
        result = dict()
        assert isinstance(usdf_model, UsdModelScene)
        usdf_model.log.info("found: {}".format(len(geomlist)))
        result = usdf_model.build_usd_model_asset(geomlist, force=force)
        usdf_model.log.info("process model: {}".format(len(result)))
        return result
