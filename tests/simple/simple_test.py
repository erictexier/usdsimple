import pytest


@pytest.mark.parametrize("a,b", [(1, 1), (2, 2), (3, 3)])
def test_simple(a, b):
    assert a == b


CSTTAG = [
    "sda::layer",
    "sda::payload",
    "sda::reference",
    "sda::sublayer",
    "sda::empty",

    "sda::stage",
    "sda::stageasset",
    "sda::stageshot",
    "sda::stagesequence",
    "sda::stagelocation",

    "sda::entry",
    "sda::entryasset",
    "sda::entryshot",
    "sda::entrysequence",
    "sda::entrylocation",

    "sda::opinion_asset",
    "sda::opinion_asset_desc",
    "sda::opinion_asset_geom",
    "sda::opinion_shot",
    "sda::opinion_shot_manifest",
    "sda::opinion_shot_geom",
    "sda::othersubLayer_Type",
]

CSTTYPE = [
    "layer",
    "payload",
    "reference",
    "sublayer",
    "empty",

    "stage",
    "stageasset",
    "stageshot",
    "stagesequence",
    "stagelocation",

    "entry",
    "entryasset",
    "entryshot",
    "entrysequence",
    "entrylocation",

    "opinionasset",
    "descriptionasset",
    "geometryasset",

    "opinionshot",
    "descriptionshot",
    "geometryshot",

    "othersublayer",
]


def test_import_xroot():
    from xcore.xscene import SCH_DEF

    cstag = [tag.replace("::", SCH_DEF.SEP) for tag in CSTTAG]

    assert cstag == [x.tag for x in SCH_DEF._all__]
    assert CSTTYPE == [x.Property for x in SCH_DEF._all__]
    key = SCH_DEF.SDAT + SCH_DEF.SEP
    for x in cstag:
        assert x.startswith(key)
    # no double
    assert len(cstag) == len(set(cstag))
    assert len(CSTTYPE) == len(set(CSTTYPE))



def test_xroot_class():
    from xcore.xscene import _XGen
    assert len(CSTTYPE) == len(_XGen.keys())
    for x in _XGen:
        assert _XGen[x]()
