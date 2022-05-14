# -*- coding: utf-8 -*-

import six
from collections import defaultdict
import json
import base64

# Local
from metaio.genericxml import GenericXml

# SCHEMA


class constant(object):
    """
    list of xmltag to map factory to
    """

    # for scenegraph
    attrlist = "arbitraryList"
    instance = "instance"
    scatter = "scatter"
    group = "group"
    scenetag = "scenegraphXML3D"
    lookfile = "lookFile"
    bounds = "bounds"
    xform = "xform"

    # new for scenegraph
    instanceanim = "instanceanim"
    instancescatter = "instancescatter"
    instanceasset = "instanceasset"
    instancecrowds = "instancecrowds"
    instancecamera = "instancecamera"
    instancemtl = "instancemtl"

    # other sub class
    attribute = "attribute"
    cameraabc = "abcAsset"
    modelfile = "modelFile"
    animcache = "animCache"
    simcache = "crowdSimCache"
    abcscatter = "abcScatter"
    assetscatter = "assetScatter"
    scat_cache = "scatcache"

    xgen = "xgen"
    xgenscalpe = "scalpCache"
    xgenmatdelta = "material_delta"
    xgendelta = "delta"
    xgenshoteditdelta = "shotEditDelta"

    # extra data key to help mat
    material = "matdata"
    matfile = "mtlfile"
    matfile_ext = ".jsonm"
    mat_subfolder = matfile_ext[1:]
    # type for the style of serialization
    encoded = "encoded"
    decoded = "decoded"
    isfile = "file"


class constant_uri(object):
    uri_uri = "bundles_uri://"
    uri_uri = "uri://"


class SceneXml(GenericXml):
    Property = "SceneXml"
    __filter = set()
    _sep = "/"

    def __init__(self, tag=None):
        super(SceneXml, self).__init__(tag)

    @classmethod
    def set_filter(cls, property_list):
        cls.__filter = set(property_list)

    def print_nice(self, max_char=120, tab=""):
        """overwrite base class
        Args:
            max_char(int): clip the value of attrib
            tab(string): indent
        """

        if self.Property in self.__filter:
            super(SceneXml, self).print_nice(max_char, tab)
        else:
            for ch in self.get_children():
                ch.print_nice(max_char=max_char, tab=tab + " " * 4)

    def get_name(self):
        if hasattr(self, "name"):
            return self.name
        return self.Property

    def set_geom_instance_data(self, geom):
        # some custom runtime data
        # not serialysed
        self._geom = geom

    def get_geom_instance_data(self):
        # not serialized
        if hasattr(self, "_geom"):
            return self._geom
        return None

    def get_path(self):
        """

        Returns:
             path from the root
        """

        parent = self.get_parent()
        if parent is None:
            return self.get_name()
        pp = parent.get_path()
        if pp != "":
            return pp + self._sep + self.get_name()
        else:
            return self.get_name()

    def delegate(self, args):
        """build a dict with _x args"""
        d = dict()
        for x in args:
            d.update({"_@x%s" % x: args.get(x, "")})
        self.__dict__.update(d)

    def get_delegate(self):
        """build a dict with _x args"""
        d = dict()
        for x in self.__dict__:
            if x.startswith("_@x"):
                d.update({x[3:]: self.__dict__[x]})
        return d

    @classmethod
    def factory(cls, default_classes, log=None, mother_class=None):
        class SceneDefault(SceneXml):
            log = None
            __doc__ = ("py representation SceneDefault",)

        if mother_class == None:
            mother_class = SceneXml
        upmethod = dict()
        class_def = list()
        for classRoot in default_classes:
            upmethod.update(
                {
                    "log": log,
                    "Property": classRoot,
                    "__doc__": "py representation %s" % classRoot,
                }
            )
            class_def.append(
                type(
                    classRoot + "Xml",
                    (mother_class,),
                    upmethod,
                )
            )
        cls.__filter.update(default_classes)
        named = [x.Property for x in class_def]
        result = dict(zip(named, class_def))
        result.update({"default": SceneDefault})
        return result


class ScenegraphXml(SceneXml):
    """Top level node for a uri queriable scenegraph (optional)"""

    Property = "root"
    __Serviceuri = None
    SUBREGION = "SUB_"

    def __init__(self, tag=constant.scenetag):
        super(ScenegraphXml, self).__init__(tag)
        self.__registered = defaultdict(list)
        # registe self as first one only
        if self.Property not in self.__registered:
            self.__registered[self.Property].append(self)

    def get_name(self):
        return ""

    def do_register_3d(self, objectprop, obj3d):
        self.__registered[objectprop].append(obj3d)

    def update_subregion(self):
        """refine do_register_3d with sub_region"""
        regions = self.__registered.get(GroupSceneXml.Property, None)
        if regions is None:
            return
        plist = [x.get_path() for x in self.__registered[GroupSceneXml.Property]]
        # reroot when come from old scenegraph
        plist = [
            x.replace(SceneXml.Property + "/", "", 1)
            if x.startswith(SceneXml.Property)
            else x
            for x in plist
        ]
        keeper = dict(zip(plist, self.__registered[GroupSceneXml.Property]))

        self.__registered[GroupSceneXml.Property] = list()
        regions = list()
        unregister = list()

        for x in plist:
            if SceneXml.Property not in x:
                # only node with not sub container are direct
                self.__registered[GroupSceneXml.Property].append(keeper[x])
                regions.append([x, keeper[x]])
                keeper.pop(x)
            else:
                unregister.append(x)

        for sub in unregister:
            for apath, deleg in regions:
                if sub.startswith(apath):
                    deleg.delegate({sub: keeper[sub]})
                    break
        # for now...
        # self.__registered[self.SUBREGION + GroupSceneXml.Property] = [keeper[x] for x in unregister]

    def get_register(self):
        return self.__registered

    @classmethod
    def set_uri(cls, scene_uri):
        """set to None to release
        Args:
            scene_uri: instance
        """
        if scene_uri is None:
            cls.__Serviceuri = None
        else:
            from metaio import sceneuri

            assert isinstance(scene_uri, sceneuri.Sceneuri)
            cls.__Serviceuri = scene_uri

    @classmethod
    def get_uri_service(cls):
        return cls.__Serviceuri

    @staticmethod
    def is_uri(ref):
        return ref.startswith(constant_uri.uri_uri)

    @staticmethod
    def is_uri(ref):
        return ref.startswith(constant_uri.uri_uri)

    @classmethod
    def get_uri_data(cls, list_of_ref):
        """Return a  model or klf
        Returns:
            dict(): empty if no uri or uri ref
        """
        result = defaultdict(list)
        if cls.__Serviceuri is None:
            return dict()
        for ref in list_of_ref:
            if cls.is_uri(ref):
                res = cls.__Serviceuri.query_uri(ref)
                for key in res:
                    if key == "model":
                        result[constant.modelfile].append(res[key])
                    elif key == "material":
                        result[constant.lookfile].append(res[key])
            elif cls.is_uri(ref):
                res = cls.__Serviceuri.query_bundle(ref)
                for key in res:
                    if key == "model":
                        result[constant.modelfile].extend(res[key])
                    elif key == "material":
                        result[constant.lookfile].extend(res[key])
        return result

    @classmethod
    def get_sub_model_info(cls, scatterfile):
        result = dict()
        if cls.__Serviceuri is None or scatterfile in [None, ""]:
            return dict()
        result = cls.__Serviceuri.gather_scatter(scatterfile)
        return result


class GroupSceneXml(SceneXml):
    """An entry point for bound box and xform of multiple instance for GEOM_3D (static)"""

    Property = "REGION_3D"

    def __init__(self, tag=constant.group):
        super(GroupSceneXml, self).__init__(tag)

    def register(self, root=None):
        if root:
            root.do_register_3d(self.Property, self)

    def get_transform_api(self):
        for ch in self.get_children():
            if ch.Property == "XFORM":
                return ch
        return None

    def get_bound_api(self):
        for ch in self.get_children():
            if ch.Property == "BOUNDS":
                return ch
        return None

    def get_asset_list(self):
        for ch in self.get_children():
            if ch.Property == "SceneXml":
                return ch.get_children()
        return None


class InstanceBoundsXml(SceneXml):
    Property = "BOUNDS"
    __keys = ["maxx", "maxy", "maxz", "minx", "miny", "minz"]

    def __init__(self, tag=constant.bounds):
        super(InstanceBoundsXml, self).__init__(tag)
        self.maxx = "0."
        self.maxy = "0."
        self.maxz = "0."
        self.minx = "0."
        self.miny = "0."
        self.minz = "0."

    def get_data(self):
        return [self.maxx, self.maxy, self.maxz, self.minx, self.miny, self.minz]

    def set_data(self, adict):
        if constant.bounds in adict:
            val = adict.pop(constant.bounds)
            assert len(val) == 6
            for i, key in enumerate(self._keys):
                self.__dict__[key] = str(val[i])
        return adict


class InstanceXformXml(SceneXml):
    Property = "XFORM"

    def __init__(self, tag=constant.xform):
        super(InstanceXformXml, self).__init__(tag)

    def get_data(self):
        return self.value

    def get_xform(self):
        return self.value

    def set_data(self, adict):
        if constant.xform in adict:
            value = adict.pop(constant.xform)
            if isinstance(value, list):
                assert len(value) == 16
                value = [str(x) for x in value]
                self.value = " ".join(value)
            else:
                assert isinstance(value, six.string_types[0])
                # we assume is correct
                self.value = value.replace(",", " ")
        return adict


class InstanceAttribXml(SceneXml):
    """Basic stupid Attribute class,  value are string with type named
    support only str, float and int for now
    """

    Property = "ATTRIBUTE"
    __maptype = {
        "int": "int",
        "str": "string",
        "unicode": "string",
        "float": "float",
        "bool": "bool",
    }

    def __init__(self, tag=constant.attribute):
        super(InstanceAttribXml, self).__init__(tag)
        self.type = "string"
        self.value = ""
        self.name = ""

    def get_data():
        return self

    def do_encode_value(self, value):
        # the test for this encoding and xml is not done TODO.
        self.value = base64.encodestring(json.dumps(value))
        self.type = constant.encoded
        return self.value

    def decode_value(self):
        self.value = json.loads(base64.decodestring(self.value))
        self.type = constant.decoded
        return self.value

    def set_data_with_type(self, args):
        try:
            name = args.pop("name")
            value = args.pop("value")
        except Exception as e:
            raise Exception("FOR NOW: {}".format(e))

        self.name = name
        if isinstance(value, dict):
            self.do_encode_value(value)
        else:

            self.type = self.__maptype[value.__class__.__name__]
            self.value = str(value)


class InstanceKlfXml(SceneXml):

    Property = "KLF"

    def __init__(self, tag=constant.lookfile):
        super(InstanceKlfXml, self).__init__(tag)
        self.ref = ""

    def get_data(self):
        if self.ref.endswith(".klf"):
            return self.ref
        parent = self.get_parent()
        if parent is None:
            return self.ref
        root = parent.get_root()
        result_query = root.get_uri_data([self.ref])
        if result_query:
            if constant.lookfile in result_query:
                return result_query[constant.lookfile][0]
        return self.ref

    def set_data(self, adict):
        if constant.lookfile in adict:
            self.ref = adict.pop(constant.lookfile)
        return adict


class InstanceMtlXml(SceneXml):
    Property = "MTL"

    def __init__(self, tag=constant.instancemtl):
        super(InstanceMtlXml, self).__init__(tag)
        self.mtl = ""
        self.coded = ""

    def do_encode_mtl(self, mtl):
        if mtl in [None, ""]:
            self.mtl = ""
            self.coded = ""
        if isinstance(mtl, dict):
            self.mtl = base64.encodestring(json.dumps(mtl))
            self.coded = constant.encoded
        else:
            assert isinstance(mtl, six.string_types[0])
            self.coded = constant.isfile
            self.mtl = mtl
        return self.mtl

    def decode_mtl(self):
        if self.coded == constant.encoded:
            self.mtl = json.loads(base64.decodestring(self.mtl))
            self.coded = constant.decoded
        return self.mtl

    def set_data(self, args):
        """set a file name or a dict value"""
        if constant.material in args:
            self.do_encode_mtl(args.pop(constant.material))
        elif constant.matfile in args:
            self.coded = constant.isfile
            self.mtl = args.pop(constant.matfile)
        return args


class InstanceSceneXml(SceneXml):
    """TODO:no mapping yet"""

    Property = "GEOM_3D"
    __root = None
    __keys = set(
        [
            constant.lookfile,
            constant.bounds,
            constant.xform,
            constant.attrlist,
            constant.instancemtl,
        ]
    )
    __factory = {
        constant.lookfile: InstanceKlfXml,
        constant.xform: InstanceXformXml,
        constant.bounds: InstanceBoundsXml,
        constant.attrlist: SceneXml,
        constant.attribute: InstanceAttribXml,
        constant.instancemtl: InstanceMtlXml,
    }

    @classmethod
    def get_factory(cls):
        return cls.__factory

    def __init__(self, tag=None):
        if tag is None:
            tag = constant.instance
        super(InstanceSceneXml, self).__init__(tag)
        self.__lookup = dict()
        self._clear_cache()
        self.refFile = ""

    def _clear_cache(self):
        for key in self.__keys:
            self.__lookup[key] = None

    def register(self, root=None):
        if root:
            if InstanceSceneXml.__root is None:
                InstanceSceneXml.__root = root
            root.do_register_3d(self.Property, self)

    @classmethod
    def get_root(cls):
        return cls.__root

    def get_model_abc(self):
        if self.__root is None:
            return self.refFile
        if self.refFile.endswith(".abc"):
            return self.refFile
        result_query = self.__root.get_uri_data([self.refFile])
        if result_query:
            # will just set the cache not the instance member
            if constant.lookfile in result_query:
                temp_kfl = self.__factory[constant.lookfile]()
                klfile = result_query[constant.lookfile][0]
                temp_kfl.set_data({constant.lookfile: str(klfile)})
                self.__lookup[constant.lookfile] = temp_kfl
            if constant.modelfile in result_query:
                return result_query[constant.modelfile][0]
        return self.refFile

    def _get_base(self, btype):
        assert btype in self.__keys
        for ch in self.get_children():
            if ch.get_tag() == btype:
                return ch
        return None

    def get_klf(self):
        value = self.__lookup[constant.lookfile]
        if value:
            return value.get_data()
        value = self._get_base(constant.lookfile)
        if value:
            self.__lookup[constant.lookfile] = value
            return value.get_data()
        # check for uribundle
        if self.__root is None:
            return ""
        result_query = self.__root.get_uri_data([self.refFile])
        if result_query:
            # will just set the cache not the instance member
            if constant.lookfile in result_query:
                klfile = str(result_query[constant.lookfile][0])
                if klfile != "":
                    temp_kfl = self.__factory[constant.lookfile]()
                    temp_kfl.set_data({constant.lookfile: klfile})
                    self.__lookup[constant.lookfile] = temp_kfl
                return klfile
        return ""

    def get_bounds(self):
        value = self.__lookup[constant.bounds]
        if value:
            return value.get_data()
        value = self._get_base(constant.bounds)
        if value:
            self.__lookup[constant.bounds] = value
            return value.get_data()
        return self.__factory[constant.bounds]().get_data()

    def get_xform(self):
        value = self.__lookup[constant.xform]
        if value:
            return value.get_data()
        value = self._get_base(constant.xform)
        if value:
            self.__lookup[constant.xform] = value
            return value.get_data()
        return None

    def _get_other(self, otype):
        for ch in self.get_children():
            if ch.get_tag() == constant.attrlist:
                for cch in ch.get_children():
                    if cch.name == otype:
                        return cch.value
        return None

    def get_attribute(self, name):
        """for now attribute of the same type will collapse"""
        for ch in self.get_children():
            for cch in ch.get_children():
                if cch.name == name:
                    return cch
        return None

    def get_attribute_list(self):
        if constant.attrlist in self.__lookup:
            alist = self.__lookup[constant.attrlist]
            if alist:
                return alist

        alist = self.__factory[constant.attrlist](tag=constant.attrlist)
        self.__lookup[constant.attrlist] = alist
        alist.verbose = False
        self.add_child(alist)
        return alist

    def get_scatter_abc(self):
        if constant.scatter in self.__lookup:
            value = self.__lookup[constant.scatter]
            if value:
                return value
        # scatter is in the arbitrary attribute
        # this is the scatter to distribute a single asset
        value = self._get_other(constant.scatter)
        if value:
            self.__lookup[constant.scatter] = value
        return value

    def set_data(self, adict):
        """Generic setter from dictionary to mimic Property = "GEOM_3D" """

        if "name" in adict:
            self.name = adict.pop("name")
        if constant.modelfile in adict:
            self.refFile = adict.pop(constant.modelfile)
            self.refType = "abc"
            self.type = "reference"

        if adict:
            for x in adict.keys():
                if x in self.__keys:
                    obj = self._get_base(x)
                    if obj is None:
                        obj = self.__factory[x]()
                        self.add_child(obj)
                    adict = obj.set_data(adict)
                    self.__lookup[x] = obj

            attrlist = self.get_attribute_list()
            chldren = attrlist.get_children()
            if chldren is None:
                for x in adict.keys():
                    attr = self.__factory[constant.attribute]()
                    attrlist.add_child(attr)
                    val = adict.pop(x)
                    attr.set_data_with_type({"name": x, "value": val})
            else:
                attrnames = dict(zip([ch.name for ch in chldren], chldren))
                for x in adict.keys():
                    if x in attrnames:
                        attr = attrnames[x]
                    else:
                        attr = self.__factory[constant.attribute]()
                        attrlist.add_child(attr)
                    val = adict.pop(x)
                    attr.set_data_with_type({"name": x, "value": val})

        return adict

    def get_mtl(self):
        """key = material_data --> value = dict
        key = mtl -> materialfile
        """
        mtlobj = None
        if constant.instancemtl in self.__lookup:
            mtlobj = self.__lookup[constant.instancemtl]
        if mtlobj is None:
            chldren = self.get_children()
            if chldren is not None:
                for obj in self.get_children():
                    if obj.Property == self.__factory[constant.instancemtl].Property:
                        mtlobj = obj
                        break
        if mtlobj is None:
            mtlobj = self.__factory[constant.instancemtl]()
            self.add_child(mtlobj)
            self.__lookup[constant.instancemtl] = mtlobj
        return mtlobj

    def set_mtl(self, adict):
        """key = material_data --> value = dict
        key = mtl -> materialfile
        """
        mtlobj = self.get_mtl()
        assert mtlobj is not None
        return mtlobj.set_data(adict)

    def add_attribute(self, name, value, atype=None):
        attrlist = self.get_attribute_list()
        chldren = attrlist.get_children()
        attrnames = dict(zip([ch.name for ch in chldren], chldren))
        if name in attrnames:
            attr = attrnames[name]
        else:
            attr = self.__factory[constant.attribute]()
            attrlist.add_child(attr)
        attr.set_data_with_type({"name": name, "value": value})

    # def set_attribute_xml(self, element):
    #    super(InstanceSceneXml, self).set_attribute_xml(element)
    #    print(self.__dict__)


class InstanceAnimSceneXml(InstanceSceneXml):
    # No uri support
    Property = "GEOM_ANIM_3D"

    def __init__(self, tag=constant.instanceanim):
        super(InstanceAnimSceneXml, self).__init__(tag)

    def get_animCache(self):
        attr = self.get_attribute(constant.animcache)
        if attr:
            return attr.value
        return ""


class InstanceCrowdsSceneXml(InstanceSceneXml):
    # No uri support
    Property = "GEOM_CROWD"

    def __init__(self, tag=constant.instancecrowds):
        super(InstanceCrowdsSceneXml, self).__init__(tag)

    def get_animCache(self):
        attr = self.get_attribute(constant.simcache)
        if attr:
            return attr.value
        return ""


class InstanceSAsset(InstanceMtlXml):
    Property = "SASSET"

    def __init__(self, tag=constant.instanceasset):
        super(InstanceSAsset, self).__init__(tag)
        self.name = ""
        self.model = ""
        self.klf = ""

    def get_klf(self):
        return self.klf

    def get_model_abc(self):
        return self.model

    def set_data(self, args):
        self.name = args.get("name", self.name)
        self.model = args.get(constant.modelfile, self.model)
        self.klf = args.get("klf", self.klf)
        super(InstanceSAsset, self).set_data(args)


class InstanceScatterSceneXml(InstanceSceneXml):
    Property = "SCATTER_3D"

    def __init__(self, tag=constant.instancescatter):
        super(InstanceScatterSceneXml, self).__init__(tag)

    def set_data(self, adict):
        """Generic setter from dictionary to mimic Property = "GEOM_3D" """
        if "name" in adict:
            self.name = adict.pop("name")
        if constant.abcscatter in adict:
            self.refFile = adict.pop(constant.abcscatter)
            self.refType = "pointabc"
            self.type = "scatter"
        if constant.assetscatter in adict:
            self.primasset = adict.pop(constant.assetscatter)
        return adict

    def get_ptc(self):
        return self.refFile

    def get_subasset_list(self):
        return filter(lambda x: x.Property == "SASSET", self.get_children())

    def set_primary_dependency(self):
        """add a node per subasset with query uri"""
        # assets = self.primasset.split(";")
        result = list()
        rootservice = self.get_root()
        if rootservice is None:
            return dict()

        adictlist = rootservice.get_sub_model_info(self.refFile)

        for asset_name in adictlist:
            assert asset_name != ""
            if len(adictlist[asset_name]) > 0:
                model = ""
                klfile = ""
                for attr in adictlist[asset_name]:
                    if constant.lookfile in attr:
                        klfile = attr[constant.lookfile]
                    elif constant.modelfile in attr:
                        model = attr[constant.modelfile]
                res = self.add_subasset(asset_name, model, klfile)
                if res:
                    result.append(res)
        return result

    def add_subasset(self, name, abcfile, klfile, mtl=None):
        """add subasset (primary asset) info as children
        Args:
            name(str): asset name
            abcfile(str):
            klfile(str):
            mtl: a dictionary (later support for mtlfile...)
        Returns:
            instance(InstanceSAsset)
        """
        chldren = self.get_children()
        subasses = dict(zip([ch.name for ch in chldren], chldren))
        # check if the subasset is in there already
        if name in subasses:
            attr = subasses[name]
        else:
            attr = InstanceSAsset()
            self.add_child(attr)
            attr.name = name
        adict = dict()
        adict[constant.modelfile] = abcfile
        adict["klf"] = klfile
        if mtl is not None:
            adict["mtl"] = mtl
        attr.set_data(adict)
        return attr


class InstanceCameraSceneXml(SceneXml):
    # No uri support
    Property = "CAMERA"

    def __init__(self, tag=constant.instancecamera):
        super(InstanceCameraSceneXml, self).__init__(tag)
        self.filepath = ""

    def register(self, root=None):
        if root:
            root.do_register_3d(self.Property, self)

    def get_camera_abc(self):
        return self.filepath

    def set_data(self, adict):
        if "name" in adict:
            self.name = adict.pop("name")
        if constant.cameraabc in adict:
            self.filepath = adict.pop(constant.cameraabc)
        return adict


### runtime
class InstanceScatCache(SceneXml):
    # not serialised for now
    """conviennience to register run time creation"""
    Property = "SCAT_CACHE"

    def __init__(self, tag=constant.scat_cache):
        super(InstanceScatCache, self).__init__(tag)
        self.geomnode = None
        self.ptcfile = ""

    def set_node_scatter(self, anode, loc_list, do_register=True):
        self.anode_with_scatter = anode
        self.ptcfile = anode.get_scatter_abc()
        self.loc_list = loc_list
        if do_register:
            try:
                root = anode.get_root()
                if root:
                    root.do_register_3d(self.Property, self)
            except Exception as e:
                raise Exception(e)

    def get_ptc(self):
        return self.ptcfile


""" This is use as argument for the api io, to pass to the reader.
Do Not modify, just add to it with new key
"""
_Generator = {
    "scenegraphXML": ScenegraphXml,
    "scenegraphXML3D": ScenegraphXml,
    "group": GroupSceneXml,
    "reference": InstanceSceneXml,
    "abc": InstanceSceneXml,
    constant.instanceanim: InstanceAnimSceneXml,
    constant.instancecrowds: InstanceCrowdsSceneXml,
    constant.instancecamera: InstanceCameraSceneXml,
    constant.instancescatter: InstanceScatterSceneXml,
    constant.instanceasset: InstanceSAsset,
    constant.instancemtl: InstanceMtlXml,
}
_Generator.update(InstanceSceneXml.get_factory())
