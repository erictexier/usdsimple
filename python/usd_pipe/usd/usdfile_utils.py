# -*- coding: utf-8 -*-

import os
import stat
import subprocess
import datetime
import json
import six
import getpass
from collections import namedtuple

import logging

from outsource import template_render_test
from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.time_utils import StopWatch

from usd_pipe.io.scenexml import ScenegraphXml
from usd_pipe.api import dskscene_api

# extension in the config manager
from config_manager import ConfigManager

bmsc_ext = ConfigManager().config("outsource", filename="dskscene")["dskscene_ext"]

logger = logging.getLogger(__name__)


class UsdFileUtils(object):

    MODELS = "usdmodels"
    ASSETS_LOCATION = "usdlayout/locations"
    ASSETS_SCATTER = "usdlayout/scatters"

    SEQUENCES = "sequences"

    _subfolder_root = "local"
    _name_scene = "scene_shot.%s" % bmsc_ext

    # option for the process to build material:
    #       no: no material scan
    #       embedded: material are saved inside the scenegraphXML3D
    #       file: save to file the material
    file_mat = "file"
    embedded_mat = "embedded"
    no_mat = "no"
    scene_type_mat = set([file_mat, embedded_mat, no_mat])

    # the build can be full or partial depending on the input file type
    # supported format tag:
    #     - xml (scenegraph)
    #     - manifest (json)
    #     - katana and livegroup (with shotin group)

    via_list = ["xml", "manifest", "json", "livegroup", "katana"]

    def __init__(self, ctx, outputdir, log=None):
        """Minimun initialization
        Args:
            ctx(context_manager.Context)
            log(logging handler)
            outputdir(str):    save directory (not in the prod tree)
        """
        self.log = logger if log is None else log
        self.ctx = ctx

        # nothing is written in the show tree
        assert not outputdir.startswith("/projects")
        assert not "prod" in outputdir

        self._outputdir = outputdir
        assert ctx.project not in (None, "")
        # clip context to project level

    def get_outdir(self):
        return self._outputdir

    def get_ctx(self):
        return self.ctx

    @classmethod
    def do_material(cls, material):
        if material in cls.scene_type_mat and material != cls.no_mat:
            return True
        return False

    @staticmethod
    def get_asset_scatter(scatfile):
        """get asset primary name on abc scatter file

        Args:
            scatfile(str): a scatter abcfile
        Returns:
            list(str): asset names
        """
        # external
        try:
            from alembic_tools import cask, util
        except:
            pass

        arc = cask.Archive(scatfile)
        asset_list = list()
        for c in util.walk(arc.top):
            if c.type() == "Xform":
                asset_list.append(c.name)
        return asset_list

    # location for resource file
    def get_output_local(self, sublocation):
        """top location (not in prod) + sublocation
        not scope by the project name
        """
        assert not sublocation in ["", None]
        assert not sublocation.startswith(os.sep)

        return os.path.join(
            self._outputdir,
            self._subfolder_root,
            os.sep.join(sublocation.split(os.sep)),
        )

    # save guard to avoid prodution tree at the moment
    def _demangler_shot(self):
        """a root top for all shot data info: not leading os.sep"""
        subfolder = self.ctx.path.replace(self.ctx.paths_dict["project"], "")
        subfolder = subfolder.replace("/prod/", "")
        assert not subfolder.startswith(os.sep)
        return subfolder

    def _demangler_asset(self):
        return "assets"

    # scenegraphXML3D
    @classmethod
    def get_scene_header_node(cls, label, material):
        """Create a ScenegraphXml
        a support for header scenegraphXML3D
        """
        # header file for extension
        master = ScenegraphXml()
        master.version = label
        assert material in cls.scene_type_mat
        master.material = material
        return master

    def _get_scene_exporter_location(self):
        subfolder = self._demangler_shot()
        return os.path.join(self._outputdir, self._subfolder_root, subfolder)

    def save_scene(self, master, in_scene, force=False, user=""):
        """ testing environment """
        folder = self._get_scene_exporter_location()
        base_scene_name = os.path.basename(in_scene)
        _, ext = os.path.splitext(base_scene_name)
        ext = ext.replace(".", "").replace("livegroup", "katana")
        if user == "":
            user = getpass.getuser()

        folder = os.path.join(folder, ext, user)

        DiskUtils.create_path_recursive(folder)
        scene_out = os.path.join(folder, self._name_scene)
        if not os.path.exists(scene_out) or force == True:
            dskscene_api.write_scene_with_header(master, scene_out, in_scene=in_scene)
            return True
        else:
            self.log.info("{} already saved use -f to force it".format(scene_out))
        return False

    def get_scene_name(self, extension="json", user=""):
        # to map the via for now:
        extension = extension.replace("manifest", "json")
        extension = extension.replace("livegroup", "katana")
        folder = self._get_scene_exporter_location()
        if user == "":
            user = self.ctx.fields["user_name"]
        folder = os.path.join(folder, extension, user)

        scene_in = os.path.join(folder, self._name_scene)
        if os.path.exists(scene_in):
            return scene_in
        return ""

    def get_scene(self, extension="json", user=""):
        scene_in = self.get_scene_name(extension, user)
        if scene_in != "":
            return dskscene_api.read_full_shot(scene_in, self.ctx)
        return None

    # location stuff
    def get_show_usd_location(self, sublocation=""):
        """ same as get_output scope the project name"""
        subfolder = self._demangler_shot()
        assert isinstance(sublocation, six.string_types)
        if sublocation.startswith(os.sep):
            sublocation = sublocation[1:]
        return os.path.join(
            self._outputdir,
            self.ctx.project,
            subfolder,
            os.sep.join(sublocation.split(os.sep)),
        )

    # asset
    def get_show_usd_asset(self, sublocation=""):
        """ same as get_output scope the project name"""
        subfolder = self._demangler_asset()
        assert isinstance(sublocation, six.string_types)
        if sublocation.startswith(os.sep):
            sublocation = sublocation[1:]
        return os.path.join(
            self._outputdir,
            self.ctx.project,
            subfolder,
            os.sep.join(sublocation.split(os.sep)),
        )

    # shot

    def get_show_usd_shot(self, sublocation=""):
        """ same as get_output scope the project name"""
        subfolder = self._demangler_shot()
        assert isinstance(sublocation, six.string_types)
        if sublocation.startswith(os.sep):
            sublocation = sublocation[1:]
        return os.path.join(
            self._outputdir,
            self.ctx.project,
            self.SEQUENCES,
            subfolder,
            os.sep.join(sublocation.split(os.sep)),
        )

    def geom_path(self, asset_path, fields):
        geom_dst = namedtuple("GeomNaming", "geom_fname root_model version",)
        fields.update({"usdstyle": "usd"})
        try:
            root_model = os.path.join(
                asset_path, fields.get("sequence"), fields.get("shot"), "model"
            )
            geom_fname = "%(shot)s_%(lod)s_v%(version)03d.geom.%(usdstyle)s" % fields

            version = "%(version)03d" % fields
        except Exception as e:
            self.log.exception(e)

        return geom_dst(geom_fname, root_model, version)

    @classmethod
    def clean_asset_instance_number(cls, aname):
        """Utils to remove instance number from asset name if possible
        Args:
            aname(str): asset's fullname blah_base_01
        Returns:
            str: the fullname without the instance number. Ex: blah_base
        """
        try:
            asset = asset_api.AssetVariant.from_instance_name(aname)
            return asset.name
        except:
            return aname

    def variant_path(self, root_path, fields, over_name):
        """Define the main naming for building a variant to a geometry in assets
        Args:
            root_path: save directory (not in the prod tree)
        Returns:
            "":       not an abc
            fullpath: the usd model path
        """
        destination = namedtuple(
            "VariantNaming",
            "name primname fromprim variant variant_fname folder  over_fname version",
        )
        try:
            variant = fields.get("variant")
            from_prim = fields.get("shot")
            prim_name = "{}_{}".format(from_prim, variant)
            fields.update({"over": over_name})
            fields.update({"usdstyle": "usd"})
            variant_fname = (
                "%(sequence)s_%(shot)s_%(datatype)s_%(variant)s_%(lod)s_v%(version)03d.%(usdstyle)s"
                % fields
            )
            overwrite_fname = (
                "%(shot)s_%(variant)s_%(lod)s_%(over)s_v%(version)03d.%(usdstyle)s"
                % fields
            )
            folder = os.path.join(
                root_path, fields.get("sequence"), fields.get("shot"), variant
            )
        except Exception as e:
            self.log.exception(e)
            return None

        return destination(
            os.path.splitext(variant_fname)[0],
            prim_name,
            from_prim,
            variant,
            variant_fname,
            folder,
            overwrite_fname,
            "v%03d" % fields.get("version"),
        )

    def create_asset_geom_from_abc(
        self, abc_file, usd_file_out, ascii=False, cmdline=True
    ):
        """ Convert abc to usd file
        Args:
            abc_file(str): an abc valid file
            usd_file_out(str): file out
            ascii(bool): if cmdLine False use to produce an ascii version
            cmdLine(bool): switch between external usdcat vs python module call
                           No working in all case, so it's always off
        """
        SW = StopWatch()
        cmdLine = True
        if cmdline:
            cmd = ["usdcat", abc_file, "-o", usd_file_out]
            self.log.info("CMD: {}".format(" ".join(cmd)))
            proc = subprocess.Popen(
                cmd, stdin=None, stdout=None, stderr=None, shell=False, close_fds=True,
            )
            if proc.wait() != 0:
                self.log.error("ERROR in {}".format(proc.returncode))
            else:
                SW.stop()
                self.log.info(
                    "Done script: {} ({:.4f} secs)".format(
                        os.path.basename(usd_file_out), SW.elapsed()
                    )
                )
        else:
            """ use a custom hack of usdcat in progress"""

            class arg_usdcat(object):
                inputFiles = [abc_file]
                out = usd_file_out
                populationMask = None
                loadOnly = False
                skipSourceFileComment = False
                flatten = True
                flattenLayerStack = False
                layerMetadata = False
                usdFormat = "usda" if ascii == True else None
                layerMetadata = None

            from usd_pipe.usd.usd_convertabc import main

            main(arg_usdcat)
            SW.stop()
            self.log.info(
                "Done usdcatpython:  {} ({:.4f} secs)".format(
                    os.path.basename(usd_file_out), SW.elapsed()
                )
            )

    ###
    # SUPPORT KATANA to query model data as ascii dictionary file
    def export_from_katana(self, script_name, input_file, material, force=False):
        """This is an initial stage to build: scenegraphXML3D  dskscene_ext : bmsc"""
        from rez.resolved_context import ResolvedContext

        packages = template_render_test.Script_PACKAGE

        rez_context = ResolvedContext(package_requests=packages)
        result = rez_context.get_environ()
        env = rez_context.get_environ()
        # add  custom resource
        local_resource = self.build_resources(force=force)
        katana_resource = env.get("KATANA_RESOURCES", "")
        if katana_resource:
            katana_resource = "{}{}{}".format(
                local_resource, os.pathsep, katana_resource
            )
        else:
            katana_resource = local_resource
        env.update({"KATANA_RESOURCES": katana_resource})
        self.log.info("katana Resources Updated")
        ff = "1" if force == True else "0"
        cmd = [
            "katana",
            "--script",
            script_name,
            str(self.ctx),
            input_file,
            material,
            self._outputdir,
            ff,
        ]

        env.update({"KATANA_RESOURCES": katana_resource})
        proc = subprocess.Popen(
            cmd,
            stdin=None,
            stdout=None,
            stderr=None,
            shell=False,
            env=env,
            close_fds=True,
        )
        if proc.wait() != 0:
            self.log.error("ERROR in {}:{}".format(script_name, proc.returncode))
        else:
            self.log.info("Done script: {}".format(os.path.basename(script_name)))

    def build_resources(self, force=False):
        """Build a resource file to render frame
        Naming is important for katana

        # bootstrap can be check before ...

        Args:
            output(dir): the top root where to write the result
        """

        RESOURCEDIR = "ResourcesDSK"
        RESOLUTIONDIR = "{}/Resolutions".format(RESOURCEDIR)
        STARTUPDIR = "{}/Startup".format(RESOURCEDIR)

        outresource = self.get_output_local("resource/katana")

        # create resource files
        resource_dir_dest = os.path.join(outresource, RESOLUTIONDIR)

        resource_file = os.path.join(resource_dir_dest, "BmResolutions.xml")
        if not os.path.exists(resource_file) or force:
            self.log.info("Building Resource: {}".format(resource_file))
            DiskUtils.create_path_recursive(resource_dir_dest)
            with open(resource_file, "w") as fout:
                fout.write(template_render_test.Render_Resource)

        # create an init file
        pyscript = template_render_test.Init_Py_Script
        pyinit_dir_dest = os.path.join(resource_dir_dest, STARTUPDIR)

        script_init = os.path.join(pyinit_dir_dest, "init.py")
        if not os.path.exists(script_init) or force:
            self.log.info("Building Init script: {}".format(script_init))
            DiskUtils.create_path_recursive(pyinit_dir_dest)
            with open(script_init, "w") as fout:
                fout.write(pyscript)

        return os.path.join(resource_dir_dest, RESOURCEDIR)
