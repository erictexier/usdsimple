# -*- coding: utf-8 -*-

import six
from datetime import datetime
import collections
from usd_pipe.io.scenexml import constant as scncst


class Scanner(object):
    """Utils to scan katana node
    Warning: keys of return dictionary are important:
    ToDo:  bind dictionary key to constant, but for now, they are in katana loader code

    notice: param.getName() are "quote", can be taken out when load build from xml
    """

    # katana node type used
    CameraLoader = "DSKCameraLoaderMacro"
    AnimationLoader = "DSKAnimationLoaderMacro"
    CrowdLoader = "DSKCrowdLoaderMacro"
    LayoutLoader = "DSKLayoutLoaderMacro"
    XGenProc = "DSKXGenProcMacro"
    TransferTransform = "DSKTransferTransformsMacro"
    Alembic_In = "Alembic_In"
    AttributeSet = "AttributeSet"

    # Katana dependant
    @classmethod
    def scan_camera(cls, nodeobj_bmcamera):
        """
        Args:
            nodeobj_bmcamera(DSKCameraLoaderMacro):
                node in SHOT_IN for alembic Camera:
        Returns:
            dict: with an 'abcAsset' (scncst.cameraabc) key the filename of the alembic
        """
        tmpresult = dict()
        for ch in nodeobj_bmcamera.getChildren():
            if ch.getType() == cls.Alembic_In:
                params = ch.getParameters().getChildren()
                for param in params:
                    if param.getName() == "abcAsset":
                        tmpresult[scncst.cameraabc] = param.getValue(0)
                        return tmpresult
        return tmpresult

    @classmethod
    def scan_scatter(cls, node):
        """
        Args:
            node(katana group node): with 'scatter' in name
        Returns:
            dict: with  scncst.abcscatter and 'assetScatter' keys
        """
        tmpresult = dict()
        params = node.getParameters().getChildren()
        for param in params:
            if param.getName() == "filepath":
                value = param.getValue(0)
                tmpresult[scncst.abcscatter] = value
                return tmpresult
        return tmpresult

    @classmethod
    def scan_animated(cls, nodeobj_bmanimation):
        """Note missing velocity, distance from camera etc...
        Args:
            nodeobj_bmanimation(DSKAnimationLoaderMacro):
        Returns:
            dict: with info on node
        """
        tmpresult = dict()
        for ch in nodeobj_bmanimation.getChildren():
            if ch.getType() == cls.Alembic_In:
                params = ch.getParameters().getChildren()
                for param in params:
                    if param.getName() == "abcAsset":
                        tmpresult[scncst.animcache] = param.getValue(0)
                        break

            elif ch.getType() == cls.TransferTransform:
                params = ch.getParameters().getChildren()
                for param in params:
                    if param.getName() == "source_file":
                        tmpresult[scncst.modelfile] = param.getValue(0)
                        break

            elif ch.getType() == cls.XGenProc:
                # xgen optional
                params = ch.getParameters().getChildren()
                tmpdic = dict()

                for param in params:
                    children = param.getChildren()
                    if children is not None:
                        param_name = param.getName()
                        # user
                        for p in children:
                            cchildren = p.getChildren()
                            if cchildren is not None:
                                for chp in cchildren:
                                    value = chp.getValue(0)
                                    if value != "":
                                        if value.endswith(".xgd"):
                                            if value.find("default_delta") != -1:
                                                tmpdic[scncst.xgenmatdelta] = value
                                            elif value.find("_delta_") != -1:
                                                tmpdic[scncst.xgendelta] = value
                                            elif value.find("shotEdit") != -1:
                                                tmpdic[scncst.xgenshoteditdelta] = value
                            else:
                                #  location xgen data
                                if p.getType() == "string":
                                    value = p.getValue(0).strip()
                                    if value != "":
                                        if value.endswith(".xgen"):
                                            tmpdic[scncst.xgen] = value
                                        elif value.endswith(".abc"):
                                            tmpdic[scncst.xgenscalpe] = value
                                        # for later
                                        else:
                                            # user_location etc.
                                            tmpdic[
                                                "%s_%s" % (param_name, p.getName())
                                            ] = p.getValue(0)
                                else:
                                    # for later user_min_pixel_width
                                    tmpdic[
                                        "%s_%s" % (param_name, p.getName())
                                    ] = p.getValue(0)

                    else:
                        pass
                        # macro, version etc.. for later
                        if param.getType() == "string":
                            value = param.getValue(0).strip()
                            if value != "":
                                tmpdic[param.getName()] = value
                        else:
                            # created_at, as a float.
                            if "created_at" == param.getName():
                                atime = datetime.utcfromtimestamp(param.getValue(0))
                                tmpdic[param.getName()] = atime.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            else:
                                tmpdic[param.getName()] = param.getValue(0)

                # update with xgen only if needed
                if scncst.xgen in tmpdic:
                    tmpresult.update(tmpdic)

            elif ch.getType() == "LookFileAssign":
                # must be a better way
                params = ch.getParameters().getChildren()
                for param in params:
                    children = param.getChildren()
                    if children is not None:
                        if param.getName() == "args":
                            for p in children:
                                for chp in p.getChildren():
                                    if chp.getName() == "asset":
                                        for xx in chp.getChildren():
                                            if xx.getName() == "value":
                                                tmpresult[
                                                    scncst.lookfile
                                                ] = xx.getValue(0)
                                            if xx.getName() == "enable":
                                                tmpresult["enable"] = (
                                                    xx.getValue(0) == 1
                                                )
                    else:
                        pass
                        # maybe needed print param, param.getValue(0), param.getValue(0) == ""
            elif ch.getType() == cls.AttributeSet:
                # LATER MaxDistanceToCam, MinDistanceToCam
                # print "XX",ch.getType(), ch.getName()
                # print ch.getParameters().getChildren()
                pass
            else:
                # other misc  katana node
                # print "XXXXX",ch.getType(), ch.getName()
                pass
        return tmpresult

    @classmethod
    def scan_layout_scene(cls, nodeobj):
        """return the xml file
        Args:
            nodeobj(DSKLayoutLoaderMacro):
        Returns:
            dict: with info on node
        """
        params = nodeobj.getParameters().getChildren()
        for param in params:
            if param.getName() == "asset":
                value = param.getValue(0)
                return value
        return ""

    @classmethod
    def _get_group_shader(cls, klfile, resolve=False):
        from Katana import FnGeolibServices

        matx = FnGeolibServices.LookFile.LookFile(filePath=klfile)
        mats = matx.getMaterials()
        # probably will need to check for list return ???
        matpath = mats.getKeys().getValue()

        matAttrGroup = matx.getMaterial(matpath)
        if resolve:
            matAttrGroup = FnGeolibServices.MaterialResolveUtil.resolveMaterialReferences(
                matAttrGroup, True
            )
        return matpath, matAttrGroup

    @classmethod
    def scan_material(cls, scenenode_or_klf, resolve=False):
        """entry point for material info for klf file or node with get_klf method
            some shader example are in /projects/pony/lib/lighting/osl/jgalonso/parallaxShader.osl
        Args:
            scenenode_or_klf(str,external object)
        Returns:
            dict: material network (or other) info
        """

        if isinstance(scenenode_or_klf, six.string_types):
            klfile = scenenode_or_klf
        else:
            klfile = scenenode_or_klf.get_klf()

        assert klfile != None
        assert klfile.endswith(".klf")

        matpath, matAttrGroup = cls._get_group_shader(klfile)
        tmpdic = dict()
        referencelist = list()
        for ch in matAttrGroup.childList():
            # key of set nodes,terminals, interface, style
            tmpdic[ch[0]] = cls._scan_material_attribute(ch[0], ch[1])
            if "reference" in tmpdic:
                ref = tmpdic.pop("reference")
                if isinstance(ref, collections.MutableMapping):
                    materialPath = ref.get("materialPath", "")
                    assetklf = ref.get("asset", "")
                    if assetklf and assetklf.endswith(".klf"):
                        ref_math_path, matAttrGroupRef = cls._get_group_shader(assetklf)
                        refdict = dict()
                        for refch in matAttrGroupRef.childList():
                            # key of set nodes,terminals, interface, style
                            refdict[refch[0]] = cls._scan_material_attribute(
                                refch[0], refch[1]
                            )
                        if len(refdict) > 0:
                            tmpdic.update({"reference:%s" % materialPath: refdict})
                        else:
                            # didn't find what reference, put it back
                            tmpdic.update({"reference:": ref})
                else:
                    # didn't find what reference, put it back
                    tmpdic.update({"reference:": ref})

        final_comp = dict()
        if len(tmpdic) > 0 and matpath != "":
            final_comp.update({"katana:%s" % matpath: tmpdic})
        return final_comp

    @staticmethod
    def _scan_material_attribute(key, mat_data):
        """scan material data
        Args:
            matdata: material (See .scan_material)
        Returns:
            dict(with terminal, style, nodes ... keys)
        """
        from Katana import FnAttribute

        adict = dict()

        if isinstance(mat_data, FnAttribute.StringAttribute):
            # type of description: network ...
            adict["mat_type"] = mat_data.getValue("")
            return adict
        for ckey, attr_data in mat_data.childList():
            adict[ckey] = dict()
            if isinstance(attr_data, FnAttribute.StringAttribute):
                adict[ckey] = attr_data.getValue("")

            elif isinstance(attr_data, FnAttribute.GroupAttribute):
                adict[ckey] = dict()

                for name_val, data_val in attr_data.childList():
                    if isinstance(data_val, FnAttribute.StringAttribute):
                        adict[ckey][name_val] = data_val.getValue("")

                    elif isinstance(data_val, FnAttribute.GroupAttribute):
                        adict[ckey][name_val] = dict()

                        for parm_name, param_val in data_val.childList():

                            if isinstance(param_val, FnAttribute.StringAttribute,):
                                adict[ckey][name_val][parm_name] = param_val.getValue(
                                    ""
                                )

                            elif isinstance(
                                param_val,
                                (
                                    FnAttribute.IntAttribute,
                                    FnAttribute.FloatAttribute,
                                    FnAttribute.DoubleAttribute,
                                ),
                            ):
                                adict[ckey][name_val][parm_name] = param_val.getData()
                                # print "INT", param_val.getNumberOfTuples(), param_val.getNumberOfValues(), param_val.getData()
                            else:
                                adict_hint = dict()
                                for ph_name, ph_val in param_val.childList():
                                    # print "\t\t\t",name_val, ph_name, ph_val.getValue("")
                                    adict_hint[ph_name] = ph_val.getValue("")
                                adict[ckey][name_val].update(adict_hint)

                    else:
                        pass
                        # print "+" * 10, data_val, type(data_val)

            else:
                pass
                # print "U" * 10, attr_data, type(attr_data)

        return adict
