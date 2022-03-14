# -*- coding: utf-8 -*-


""" To find out what to build from bams 
Support single shot or list of single shot, playlist id

"""
import os

from outsource.gatekeeper import shotfile
from outsource.gatekeeper import gate_keeper

from usd_pipe.usd import usdfile_utils
from usd_pipe.api import dskscene_api
from collections import defaultdict


class GatekeeperApi(usdfile_utils.UsdFileUtils):
    def __init__(self, ctx, outputdir, log):
        super(GatekeeperApi, self).__init__(ctx, outputdir, log)
        self._scenes = list()

    def _launch_build(self, scene_file, material, force):
        """ launch scanning to build bmsc, if material != "no", will scan in katana to
            extract mtl info else scan the manifest and/or the scene graph
        Args:
            scene_file(str): filename (json, xml, katana/livegroup)
            material(str): token: no, embedded or file
            force(bool): force the update of bmsc
        """

        if (
            self.do_material(material)
            or scene_file.endswith("katana")
            or scene_file.endswith("livegroup")
        ):
            from usd_pipe.io import katana_klf

            script_name = katana_klf.__file__.replace(".pyc", ".py")
            self.export_from_katana(script_name, scene_file, material, force)
        else:
            # the result will be cache in a bmsc scene.
            dskscene_api.SceneBuilder().load_and_process(
                self.ctx,
                scene_file,
                material,
                self.get_outdir(),
                dskscene_api.ScannerDefault,
                force,
            )

    def get_bmsc_file(self, via, material, force):
        """ Build if not exist an XmlScene3D
        Args:
            via(str): json, xml, katana
            material(str): file, no, encoded
            force(bool): even if exists rebuild the scene
        Returns:
            dict:  key:via, value: name of the input file found to build the scene
        """
        assert via in usdfile_utils.UsdFileUtils.via_list
        assert material in usdfile_utils.UsdFileUtils.scene_type_mat
        # the search here can be less restrictive (it's per user...)
        ascene = self.get_scene_name(via)
        input_file_lookup = defaultdict(list)

        if os.path.exists(ascene):
            if force == False:
                self.log.info("Done: {} exists. Used --force to update".format(ascene))
                input_file_lookup[via].append(ascene)
            # get the scene that needs to be updated
            else:
                header = dskscene_api.get_header_info(ascene)
                if "from_scene" in header:
                    in_scene = header.pop("from_scene")
                    if in_scene and os.path.exists(in_scene):
                        input_file_lookup[via].append(in_scene)
                        self._launch_build(in_scene, material, force=force)
            return input_file_lookup

        # we didn't found the scene, use gate keeper
        all_shot = list()
        if self.ctx.shot:
            all_shot, _ = shotfile.get_shotfiles(self.ctx, [self.ctx.shot])
            if len(all_shot) > 0:
                # found json
                in_scene = all_shot[0]
                if via in ["json", "manifest"]:
                    input_file_lookup[via].append(in_scene)
                    self._launch_build(in_scene, material, force=force)
                elif via == "xml":
                    header_json = dskscene_api.get_main_files_manifest(in_scene)
                    if dskscene_api.SchemaScene.layout in header_json:
                        for data in header_json[dskscene_api.SchemaScene.layout]:
                            for dname in data:
                                if "output" in data[dname]:
                                    xml_file = data[dname]["output"]
                                    if xml_file and os.path.exists(xml_file):
                                        self._launch_build(
                                            xml_file, material, force=force,
                                        )
                                        input_file_lookup[via].append(xml_file)
                elif via in ["katana", "livegroup"]:
                    gateobj = gate_keeper.GateKeeper(self.ctx)
                    kata = gateobj.get_main_lighting_files(in_scene)
                    katfile = ""
                    if via == "katana" and "katana" in kata:
                        katfile = kata[via]
                    if via == "livegroup" and "livegroup" in kata:
                        katfile = kata[via]
                    if katfile != "" and os.path.exists(katfile):
                        self._launch_build(katfile, material, force=force)
                        input_file_lookup[via].append(katfile)

        return input_file_lookup
