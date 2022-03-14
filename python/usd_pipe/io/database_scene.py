# -*- coding: utf-8 -*-

import os
from collections import defaultdict

# DSK
import bams_client
from bams_client.entity.output import UriResolutionMode
from bams_client import api
from bams_client import resolver
import bams_client.entity.uri as bams_uri

import logging
logger = logging.getLogging(__name__)


class SceneBams(object):
    """ Not Done """

    _BC = bams_client.BamsClient()

    def __init__(self, ctx):
        self.ctx = ctx

    # ASSET
    @classmethod
    def query_bams(cls, bams_url_name):
        """Query Bams for bams abc and klf file
        Args:
            bams_url_name(str): an uri bams
        Returns:
            dict: a file with klf or abc, key = datatype
        """
        entities = cls._BC.Output.resolve_asset_uri(
            bams_url_name,
            UriResolutionMode.approved_or_latest,
            expand_relative_path=True,
        )
        if len(entities):
            return dict({entities[0].datatype: entities[0].filepath})
        return dict()

    def query_bundle(self, uri_bundle_name):
        """Query Bams for bundle file. Some item require to be parse since
            it has file dependencies.  ex: klf, delta ...
        Args:
            uri_bundle_name(str): an uri bundle
        Returns:
            dict:  items type, file_path in the bundle as list (often 1 element)
        """
        result = defaultdict(list)

        bundle = bams_uri.BundleURI.resolve(
            uri_bundle_name, ctx=self.ctx, resolution_mode="latest_approved"
        )
        if bundle:
            # TODO check the mapping with scncst validity
            try:
                bundle_items = self._BC.Bundle.outputs_from_items(bundle.items)
                for item in bundle_items:
                    result[item.datatype].append(item.filepath)
            except Exception as e:
                logger.exception("in query bundle {}".format(str(e)))
        else:
            logger.error("Found a bundle null: {}".format(uri_bundle_name))
        return result

    def gather_scatter(self, scatter_file_abc):
        """Take an scatter file and return all needed abc + klf needed

        Args:
            scatter_file_abc(str): an abc file
        Returns:
            defaultdict(dict) [subassetname][model|material] = filepath
        """
        from usd_pipe.io.scenexml import constant as scncst

        assert self.ctx.project != ""
        # this is a bug
        # if "DSK_PROJECT" not in os.environ:
        os.environ["DSK_PROJECT"] = self.ctx.project
        os.environ["DSK_SEQUENCE"] = self.ctx.sequence
        os.environ["DSK_SHOT"] = self.ctx.shot
        result = defaultdict(list)
        # try to get read of a warning
        import asset_api.scatter_asset_data as scatter_api

        if not scatter_file_abc.endswith(".abc"):
            return result
        scatter = scatter_api.ScatterFile(scatter_file_abc)

        for sub_asset in scatter.get_sub_assets():
            if sub_asset.material_product.filepath:
                result[sub_asset.name].append(
                    {scncst.lookfile: sub_asset.material_product.filepath}
                )
            if sub_asset.model_product:
                result[sub_asset.name].append(
                    {scncst.modelfile: sub_asset.model_product.filepath}
                )
        return result

    def get_asset_model_path(self, asset_name):
        """Use asset_api to get the model path to an asset
        Args:
            asset_name(str): the name of the asset
        Returns:
            str(a path) or None if not found
        """
        import asset_api

        try:
            asset = asset_api.AssetVariant.from_shotgun_name(
                asset_name, project=self.ctx.project
            )
            if asset:
                model = asset.get_products({"datatype": "model", "lod": "mid"})
                return model[0].filepath
        except Exception as e:
            logger.error("No asset model path found: {}".format(str(e)))
        return ""

    # SHOT
    def get_camera_bams(self, name):
        return name

    def get_anim_bams(self, name):
        return name

    def get_camera_bundle(self, name):
        return name

    def get_anim_bundle(self, name):
        return name
