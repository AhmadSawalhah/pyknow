import pytest
from hypothesis import given
from hypothesis import strategies as st


def test_factlist_exists():
    try:
        from pyknow import factlist
    except ImportError as exc:
        assert False, exc
    else:
        assert True


def test_FactList_exists():
    from pyknow import factlist

    assert hasattr(factlist, 'FactList')


def test_FactList_is_class():
    from pyknow.factlist import FactList

    assert isinstance(FactList, type)


def test_FactList_has_declare_method():
    """Using declare because assert is a python keyword."""
    from pyknow.factlist import FactList

    assert hasattr(FactList, 'declare')


@given(data=st.one_of(st.integers(),
                      st.booleans(),
                      st.floats(),
                      st.complex_numbers(),
                      st.tuples(st.text()),
                      st.lists(st.text()),
                      st.sets(st.text()),
                      st.text(),
                      st.dictionaries(keys=st.text(), values=st.text())))
def test_FactList_declare_reject_not_Fact_subclass(data):
    from pyknow.factlist import FactList

    fl = FactList()
    with pytest.raises(ValueError):
        fl.declare(data)


def test_FactList_declare_allow_Fact_instances():
    from pyknow.factlist import FactList
    from pyknow.fact import Fact

    f = Fact()
    fl = FactList()

    fl.declare(f)


def test_FactList_declare_allow_Fact_subclasses():
    from pyknow.factlist import FactList
    from pyknow.fact import Fact

    class OtherFact(Fact):
        pass

    f = OtherFact()
    fl = FactList()

    fl.declare(f)


def test_FactList_declare_returns_idx():
    from pyknow.factlist import FactList
    from pyknow.fact import Fact

    f0 = Fact(data=1)
    f1 = Fact(data=2)

    fl = FactList()

    assert fl.declare(f0) == 0
    assert fl.declare(f1) == 1


def test_FactList_declare_returns_None_if_fact_already_exists():
    from pyknow.factlist import FactList
    from pyknow.fact import Fact

    f0 = f1 = Fact(data=1)
    fl = FactList()

    assert fl.declare(f0) == 0
    assert fl.declare(f1) is None


def test_FactList_retract_exists():
    from pyknow.factlist import FactList

    assert hasattr(FactList, 'retract')


@given(idx=st.integers())
def test_FactList_retract_unknown_index_raise_IndexError(idx):
    from pyknow.factlist import FactList

    fl = FactList()

    with pytest.raises(IndexError):
        fl.retract(idx)


def test_FactList_cant_retract_twice():
    from pyknow.factlist import FactList
    from pyknow.fact import Fact

    f0 = Fact()
    fl = FactList()
    idx = fl.declare(f0)

    fl.retract(idx)
    with pytest.raises(IndexError):
        fl.retract(idx)
