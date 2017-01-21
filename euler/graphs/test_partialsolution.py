from pytest import raises
from .cycles import PartialSolution, PathSet

simple_ps = PartialSolution(PathSet([('a', 'b')]), [])
simple_ps_with_isolated = PartialSolution(PathSet([('a', 'b'), ('c', 'd')]), ['e', 'f'])


def test_egalite():
    assert PartialSolution(PathSet([('b', 'a'), ('c', 'd')]), {'e'}) == PartialSolution(
        PathSet([('c', 'd'), ('a', 'b')]), {'e'})


def test_simple_single_extension():
    res = simple_ps_with_isolated.extend_single_points({'e': ['g', 'h'], 'f': ['i', 'j']})

    assert res is not None
    assert res.arcs() == frozenset([('a', 'b'), ('c', 'd'), ('g', 'h'), ('i', 'j')])


def test_no_single_extension():
    res = simple_ps_with_isolated.extend_single_points({'e': ['f'], 'f': ['i', 'j']})
    assert res is None

    res = simple_ps_with_isolated.extend_single_points({'e': ['f', 'g'], 'f': []})
    assert res is None


def test_single_cycle():
    with raises(ValueError):
        simple_ps_with_isolated.extend_single_points({'e': ['a', 'b'], 'f': ['i', 'j']})


def test_simple_arc_extension():
    res = list(simple_ps.successors({'c', 'd', 'e'}, {'a': 'c', 'b': 'd'}))

    assert len(res) == 1
    assert len(res[0]) == 2
    assert res[0][1] == 0
    assert res[0][0] == PartialSolution(PathSet([('c', 'd')]), {'e'})


def test_more_complicated_extension():
    ps = PartialSolution(
        PathSet([('a', 'b'), ('c', 'd')]), {'e'}
    )

    successors = list(ps.successors(
        ['f', 'g', 'h', 'i', 'j', 'k'],
        {'a': ['f', 'g'], 'b': ['h'], 'c':  ['i'], 'd': ['j'], 'e': ['g', 'h']},
    ))

    assert len(successors) == 2, "there should be two ways to prolong this partial solution"

    assert successors[0][1] == 0
    assert successors[0][0] == PartialSolution(PathSet([('f', 'g'), ('i', 'j')]), {'k'})

    assert successors[1][1] == 1
    assert successors[1][0] == PartialSolution(PathSet([('i', 'j')]), {'k', 'f'})


def test_very_complicated_extension():
    ps = PartialSolution(
        PathSet([('a', 'b'), ('c', 'd')]),
        {'e', 'f'}
    )

    next_partition = ['g', 'h', 'i', 'j', 'k', 'l']
    forward_arcs = {
        'a': ['i'], 'b': ['g', 'j'], 'c':['g', 'k'], 'd': ['h'], 'e': ['h', 'j'], 'f': ['i', 'k']
    }

    successors = frozenset(ps.successors(next_partition, forward_arcs))

    assert successors == {
        (PartialSolution(PathSet([('k', 'j')]), {'l'}), 0),
        (PartialSolution(PathSet([('g', 'j')]), {'l'}), 0),
        (PartialSolution(PathSet([('g', 'k')]), {'l'}), 0),
        (PartialSolution(PathSet([]), {'g', 'l'}), 1),
    }
