from pytest import raises
from .cycles import PartialSolution, PathSet
from .grid import code

simple_ps = PartialSolution(PathSet([('a', 'b')]), [])
simple_ps_with_isolated = PartialSolution(PathSet([('a', 'b'), ('c', 'd')]), ['e', 'f'])


def test_egalite():
    assert PartialSolution(PathSet([('b', 'a'), ('c', 'd')]), {'e'}) == PartialSolution(
        PathSet([('c', 'd'), ('a', 'b')]), {'e'})


def test_simple_single_extension():
    res, reached = simple_ps_with_isolated.extend_single_points({'e': ['g', 'h'], 'f': ['i', 'j']})

    assert res is not None
    assert res.arcs() == frozenset([('a', 'b'), ('c', 'd'), ('g', 'h'), ('i', 'j')])
    assert reached == {'g', 'h', 'i', 'j'}


def test_no_single_extension():
    res = simple_ps_with_isolated.extend_single_points({'e': ['f'], 'f': ['i', 'j']})
    assert res == (None, None)

    res = simple_ps_with_isolated.extend_single_points({'e': ['f', 'g'], 'f': []})
    assert res == (None, None)


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
        {'a': ['f', 'g'], 'b': ['h'], 'c': ['i'], 'd': ['j'], 'e': ['g', 'h']},
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
        'a': ['i'], 'b': ['g', 'j'], 'c': ['g', 'k'], 'd': ['h'], 'e': ['h', 'j'], 'f': ['i', 'k']
    }

    successors = frozenset(ps.successors(next_partition, forward_arcs))

    assert successors == {
        (PartialSolution(PathSet([('k', 'j')]), {'l'}), 0),
        (PartialSolution(PathSet([('g', 'j')]), {'l'}), 0),
        (PartialSolution(PathSet([('g', 'k')]), {'l'}), 0),
        (PartialSolution(PathSet([]), {'g', 'l'}), 1),
    }

def test_neighbouring_singles():
    ps = PartialSolution(
        PathSet([]), {'a', 'b'}
    )

    next_partition = ['c', 'd', 'f']
    forward_arcs = {'a': ['c', 'd'], 'b': ['d', 'f']}

    successors = frozenset(ps.successors(next_partition, forward_arcs))

    assert successors == {
        (PartialSolution(PathSet([('c', 'f')]), {}), 0),
    }


partition_5 = {code(j, 4-j) for j in range(5)}
partition_6 = {code(j, 5-j) for j in range(6)}
forward_arcs_5 = {code(j, 3-j): [code(j+1, 3-j), code(j, 4-j)] for j in range(4)}
forward_arcs_6 = {code(j, 4-j): [code(j+1, 4-j), code(j, 5-j)] for j in range(5)}

def test_variants5_1():
    ps = PartialSolution(
        PathSet([('a3', 'b2')]), {'d0'}
    )

    assert set(ps.successors(partition_5, forward_arcs_5)) == {
        (PartialSolution(PathSet([('d1', 'e0'), ('a4', 'b3')]), {'c2'}), 0),
        (PartialSolution(PathSet([('d1', 'e0'), ('a4', 'c2')]), {'b3'}), 0),
        (PartialSolution(PathSet([('d1', 'e0'), ('b3', 'c2')]), {'a4'}), 0),
        (PartialSolution(PathSet([('d1', 'e0'),]), {'a4', 'c2'}), 1),
    }

def test_variants5_2():
    ps = PartialSolution(
        PathSet([('a3', 'c1')]), {'d0'}
    )

    assert set(ps.successors(partition_5, forward_arcs_5)) == {
        (PartialSolution(PathSet([('d1', 'e0'), ('a4', 'c2')]), {'b3'}), 0),
        (PartialSolution(PathSet([('d1', 'e0'), ('b3', 'c2')]), {'a4'}), 0),
        (PartialSolution(PathSet([('a4', 'e0')]), {'b3', 'c2'}), 0),
        (PartialSolution(PathSet([('b3', 'e0'),]), {'a4', 'c2'}), 0),
    }


# TODO these tests !

# def test_variant6_1():
#     ps = PartialSolution(
#         PathSet([('a4', 'e0')]), {'b3', 'c2'}
#     )
#
#     assert set(ps.successors(partition_6, forward_arcs_6)) == {
#         (PartialSolution(PathSet([]), {}), 0),
#     }
#
# def test_variant6_2():
#     ps = PartialSolution(
#         PathSet([('a4', 'e0')]), {'b3', 'd1'}
#     )
#
#     assert set(ps.successors(partition_6, forward_arcs_6)) == {
#
#     }
#
# def test_variant6_3():
#     ps = PartialSolution(
#         PathSet([('a4', 'c2')]), {'b3', 'e0'}
#     )
#
#     assert set(ps.successors(partition_6, forward_arcs_6)) == {
#
#     }
#
# def test_variant6_4():
#     ps = PartialSolution(
#         PathSet(), {'a4', 'b3', 'e0'}
#     )
#
#     assert set(ps.successors(partition_6, forward_arcs_6)) == {
#
#     }

# problematique : (PathSet(frozenset({('b5', 'd3')})), frozenset())
# ancêtre : PathSet(frozenset({('a5', 'f0'), ('b4', 'd2')})), frozenset({'e1', 'c3'})
# racine : PartialSolution(PathSet(frozenset({('a4', 'e0')})), frozenset({'c2', 'b3'}))