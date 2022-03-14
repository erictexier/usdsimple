# -*- coding: utf-8 -*-

import os
import re
from collections import defaultdict
from collections import namedtuple

# prx
from pxr import Kind, Sdf, Usd, UsdGeom, Gf

# DSK
from context_manager import Context

# local
from usd_pipe.usd.usdfile_utils import UsdFileUtils
from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.time_utils import StopWatch


class UsdModelScene(UsdFileUtils):
    """populate the assets models area with usd file:
    Create them all as variant of a geometry exported from abc
    """

    AssetFolder = UsdFileUtils.MODELS

    # loose for basename
    _version_pat = re.compile(r"v[\d]+")

    def __init__(self, ctx, outputdir, log):
        super(UsdModelScene, self).__init__(ctx, outputdir, log)

    def build_usb_model_asset(self, nodelist, ascii=True, force=False):
        """build geom, geomvar (variance) and asset usd  model
        Args:
            nodelist(list): list of instance (anim, model ....)
            force(bool): if True and file exists, update
        Returns:
            dict():  key: instance name
                     value: the usb model asset
        """
        SW = StopWatch()
        SW1 = StopWatch()
        all_naming = {}
        asset_path = self.get_show_usd_asset(UsdModelScene.AssetFolder)

        Lookup_as = namedtuple("Igeom", "instance_variant instance_number type node")
        Lookup_fields = namedtuple("Allgeom", "igeom mdestination vdestination")

        avoid_twice = set([])
        split_dict = defaultdict(list)

        # for now, let's reset the instancing so, there is no issue later
        # except for crowds that seams to be fine.
        instance_index = dict()

        for anode in nodelist:
            # narrow asset with asset instance number
            # eptBushQ_base_150, eptTinHatA_base_2, epGenericFemale_gTinHat_92001;crowdField1
            node_name = anode.name
            crowdfield = ""
            indexinst = ""
            if ";" in node_name:
                instance_variant, crowdfield = node_name.rsplit(";", 1)
                instance_variant, indexinst = instance_variant.rsplit("_", 1)
            else:
                res = node_name.rsplit("_", 1)
                if len(res) == 2:
                    instance_variant, indexinst = res
                else:
                    instance_variant = res[0]
                if instance_variant in instance_index:
                    instance_index[instance_variant] = (
                        instance_index[instance_variant] + 1
                    )
                    indexinst = str(instance_index[instance_variant])
                else:
                    instance_index[instance_variant] = 0
                    indexinst = "0"
                anode.name = "%s_%s" % (instance_variant, indexinst)

            ass_query = Lookup_as(instance_variant, indexinst, crowdfield, anode)
            split_dict[ass_query.instance_variant].append(ass_query)

        full_dict = dict()
        convert_list = dict()
        SW1.stop()
        self.log.info("Duration prep: {:.4f} seconds".format(SW1.elapsed()))
        SW1 = StopWatch()
        path_dict = {}

        for primgeom in split_dict:
            for ass_query in split_dict[primgeom]:
                from_asset_abc_path = ass_query.node.get_model_abc()
                if not from_asset_abc_path.endswith(".abc"):
                    self.log.error(
                        "No supported in build_usb_model_asset {}".format(
                            from_asset_abc_path
                        )
                    )
                    continue
                if from_asset_abc_path in path_dict:
                    dst_geom, dstvar = path_dict[from_asset_abc_path]
                else:
                    # ctx = Context.from_path(from_asset_abc_path, validate=False)
                    _, fields = self.ctx.path_resolver.fields_from_path(
                        from_asset_abc_path
                    )
                    dst_geom = self.geom_path(asset_path, fields)
                    DiskUtils.create_path_recursive(dst_geom.root_model)
                    filepathout = os.path.join(dst_geom.root_model, dst_geom.geom_fname)
                    convert_list.update({filepathout: from_asset_abc_path})
                    dstvar = self.variant_path(asset_path, fields, "basevar")
                    path_dict[from_asset_abc_path] = [dst_geom, dstvar]

                ass_query.node.set_geom_instance_data(
                    Lookup_fields(ass_query, dst_geom, dstvar)
                )
                # this truly rely on instance name being unique... check to do in XmlScene (Not done)
                # this is done for consistancy, but relevant data are also cache in each node (set_geom_instance_data)
                if not ass_query.node.name in all_naming:
                    all_naming[ass_query.node.name] = os.path.join(
                        dstvar.folder, dstvar.variant_fname
                    )
                else:
                    count += 1
                    self.log.error(
                        "instance with same name {}".format(ass_query.node.name)
                    )
        if count != 0:
            self.log.error("collapsing issues: %d" % count)
        SW1.stop()
        self.log.info("Duration query: {:.4f} seconds".format(SW1.elapsed()))
        SW1 = StopWatch()

        # convert all the abc
        if force == True:
            for dest in convert_list:
                # the initial _geom is built with a call to usdcat.
                self.create_asset_geom_from_abc(convert_list[dest], dest, ascii=ascii)
        else:
            for dest in convert_list:

                if not os.path.exists(dest):
                    # the initial _geom is built with a call to usdcat.
                    self.create_asset_geom_from_abc(
                        convert_list[dest], dest, ascii=ascii
                    )
        SW1.stop()
        self.log.info(
            "Duration convert abc to .usb: {:.4f} minutes".format(SW1.elapsed() / 60.0)
        )
        SW1 = StopWatch()
        # create variance
        for igeom in split_dict:
            anode = split_dict[igeom][0].node
            instance = anode.get_geom_instance_data()
            if instance:
                self.create_asset_variant(instance, force)
                self.add_variant(instance, force)
        SW1.stop()
        self.log.info(
            "Duration convert model to scene .usb: {:.2f} minutes".format(
                SW1.elapsed() / 60.0
            )
        )

        SW.stop()
        self.log.info(
            "Duration model_asset: {:.2f} minutes".format(SW.elapsed() / 60.0)
        )
        return all_naming

    def add_variant(self, instance, force):
        dest = instance.vdestination
        assetFilePath = os.path.join(dest.folder, dest.over_fname)
        if os.path.exists(assetFilePath) and force == False:
            return
        stage = Usd.Stage.CreateNew(assetFilePath)
        stage.GetRootLayer().defaultPrim = instance.igeom.instance_variant
        self._AddOver(stage, instance)
        stage.GetRootLayer().Save()

    def _AddOver(self, stage, instance):
        dest = instance.vdestination
        model = stage.OverridePrim("/%s" % instance.igeom.instance_variant)

        # if we can do this on a xform (else see traverse)
        allmesh = stage.OverridePrim("/%s/geo" % instance.igeom.instance_variant)
        var_color = Gf.ConvertDisplayToLinear(Gf.Vec3f(0.676, 0.212, 0.141))
        shadingVariant = model.GetVariantSets().AddVariantSet("shadingVariant")
        variantName = dest.variant
        # switch to that variant
        shadingVariant.SetVariantSelection(variantName)

        with shadingVariant.GetVariantEditContext():
            # set the display color for hydra
            UsdGeom.Gprim(allmesh).CreateDisplayColorAttr([var_color])
            pass

        # now make the variant selection 'Cue' instead of the last variant that we
        # created above.
        shadingVariant.SetVariantSelection(variantName)

    def create_asset_variant(self, instance, force):

        dest = instance.vdestination
        assetFilePath = os.path.join(dest.folder, dest.variant_fname)

        if os.path.exists(assetFilePath) and force == False:
            return

        rootLayer = Sdf.Layer.CreateNew(assetFilePath, args={"format": "usda"})
        assetStage = Usd.Stage.Open(rootLayer)

        # Define a prim for the asset and make it the default for the stage.
        assetPrim = UsdGeom.Xform.Define(assetStage, "/%s" % dest.primname).GetPrim()
        assetStage.SetDefaultPrim(assetPrim)
        # Lets viewing applications know how to orient a free camera properly
        UsdGeom.SetStageUpAxis(assetStage, UsdGeom.Tokens.y)

        model = Usd.ModelAPI(assetPrim)
        model.SetKind(Kind.Tokens.component)

        model.SetAssetName(dest.primname)
        model.SetAssetIdentifier(os.path.join(dest.folder, dest.variant_fname))

        self.add_variant_ref(assetPrim, instance)

        assetPrim.GetReferences().AddReference(
            "../model/%s" % instance.mdestination.geom_fname
        )
        # save  usd
        assetStage.GetRootLayer().Save()

    def add_variant_ref(self, assetPrim, instance):
        # the reference is build in add_variant
        dest = instance.vdestination
        stage_ref = Usd.Stage.CreateNew(os.path.join(dest.folder, dest.over_fname))
        referencedAssetPrim = stage_ref.DefinePrim(assetPrim.GetPath())
        stage_ref.SetDefaultPrim(referencedAssetPrim)
        assetPrim.GetReferences().AddReference(
            "./%s" % instance.vdestination.over_fname
        )
