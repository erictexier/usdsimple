import pytest

@pytest.mark.parametrize("a,b", [(1,1), (2, 2), (3,3)])
def test_simple(a, b):
    assert a == b

def test_import_xroot():
    from ucore.xroot import XassetOpinion
    opt = XassetOpinion("top", "astep", "original")