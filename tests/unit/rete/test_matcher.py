import pytest

from pyknow.abstract import AbstractMatcher


@pytest.mark.wip
def test_retematcher_exists():
    try:
        from pyknow.rete import ReteMatcher
    except ImportError as exc:
        assert False, exc


@pytest.mark.wip
def test_retematcher_is_matcher():
    from pyknow.rete import ReteMatcher

    assert issubclass(ReteMatcher, AbstractMatcher)


@pytest.mark.wip
def test_retematcher_is_not_abstract():
    from pyknow.rete import ReteMatcher
    from pyknow.engine import KnowledgeEngine

    # MUST NOT RAISE
    ReteMatcher(KnowledgeEngine())


@pytest.mark.wip
def test_retematcher_has_root_node():
    from pyknow.rete import ReteMatcher
    from pyknow.engine import KnowledgeEngine
    from pyknow.rete.nodes import BusNode

    matcher = ReteMatcher(KnowledgeEngine())
    assert hasattr(matcher, 'root_node')
    assert isinstance(matcher.root_node, BusNode)


@pytest.mark.wip
def test_retematcher_changes_are_propagated(TestNode):
    from pyknow.engine import KnowledgeEngine
    from pyknow.fact import Fact
    from pyknow.rete import ReteMatcher
    from pyknow.rete.token import Token

    matcher = ReteMatcher(KnowledgeEngine())
    tn1 = TestNode()
    tn2 = TestNode()

    matcher.root_node.add_child(tn1, tn1.activate)
    matcher.root_node.add_child(tn2, tn2.activate)

    f1 = Fact(a=1)
    f2 = Fact(b=2)
    f3 = Fact(c=3)
    f4 = Fact(d=4)

    matcher.changes(adding={f1, f2},
                    deleting={f3, f4})

    assert Token.valid(f1) in tn1.added
    assert Token.valid(f1) in tn2.added
    assert Token.valid(f2) in tn1.added
    assert Token.valid(f2) in tn2.added
    assert Token.invalid(f3) in tn1.added
    assert Token.invalid(f3) in tn2.added
    assert Token.invalid(f4) in tn1.added
    assert Token.invalid(f4) in tn2.added


@pytest.mark.wip
def test_retematcher_changes_return_activations_if_csn():
    from pyknow.engine import KnowledgeEngine
    from pyknow.fact import Fact
    from pyknow.rule import Rule
    from pyknow.activation import Activation
    from pyknow.rete.nodes import ConflictSetNode
    from pyknow.rete import ReteMatcher

    matcher = ReteMatcher(KnowledgeEngine())
    rule = Rule()
    csn = ConflictSetNode(rule)
    matcher.root_node.add_child(csn, csn.activate)

    activations = matcher.changes(adding={Fact(a=1),
                                          Fact(b=2)})

    assert len(activations) == 2
    assert all(isinstance(a, Activation) for a in activations)

#
# TODO (@dfrancos) walking into the engine building the network
#
