import pytest


@pytest.mark.parametrize("a,b", [(1, 1), (2, 2), (3, 3)])
def test_simple(a, b):
    assert a == b


CSTTAG = [
    "sda::payload",
    "sda::reference",
    "sda::sublayer",
    "sda::empty",
    "sda::asset",
    "sda::shot",
    "sda::seq",
    "sda::entry",
    "sda::opinion_asset",
    "sda::opinion_asset_desc",
    "sda::opinion_asset_geom",
    "sda::opinion_shot",
    "sda::opinion_shot_manifest",
    "sda::opinion_shot_geom",
    "sda::sublayer_type",
]

CSTTYPE = [
    "payload",
    "reference",
    "sublayer",
    "empty",
    "asset",
    "shot",
    "sequence",
    "entry",
    "opinionasset",
    "descriptionasset",
    "geometryasset",
    "opinionshot",
    "descriptionshot",
    "geometryshot",
    "sublayer",
]


def test_import_xroot():
    from xcore.xscene import SCH_DEF

    cstag = [tag.replace("::", SCH_DEF.SEP) for tag in CSTTAG]

    assert cstag == [x.tag for x in SCH_DEF._all__]
    assert CSTTYPE == [x.type for x in SCH_DEF._all__]
    key = SCH_DEF.SDAT + SCH_DEF.SEP
    for x in cstag:
        assert x.startswith(key)


def test_xroot_class():
    pass
