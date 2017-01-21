from .cycles import PathSet, normalize_path
from pytest import raises

simple_pathset = PathSet([('a', 'b'), ('c', 'd')])

complex_paths = [(i, j) for i, j in zip(range(0, 200, 2), range(1, 200, 2))]


def test_normalize_path():
    assert normalize_path(('a', 'b')) == ('a', 'b')
    assert normalize_path(('b', 'a')) == ('a', 'b')
    assert normalize_path(((0,1), (2,1))) == ((0,1), (2,1))


def test_arcs():
    arcs = simple_pathset.arcs()
    assert arcs == {('a', 'b'), ('c', 'd')}


def test_points():
    points = simple_pathset.points()
    assert set(points) == {'a', 'b', 'c', 'd'}


def test_complex_points():
    points = PathSet(complex_paths).points()
    assert set(points) == set(range(200))


def test_simple_ajout():
    res, cycling = simple_pathset.add(('e', 'f'))

    assert res.arcs() == {('a', 'b'), ('c', 'd'), ('e', 'f')}
    assert not cycling

def test_simple_extension():
    res, cycling = simple_pathset.add(('a', 'e'))

    assert res.arcs() == {('b', 'e'), ('c', 'd')}
    assert not cycling

def test_simple_cycle():
    res, cycling = simple_pathset.add(('b', 'a'))

    assert res.arcs() == {('c', 'd')}
    assert cycling


def test_double_extension():
    res, cycling = simple_pathset.add(('b', 'c'))

    assert res.arcs() == {('a', 'd')}
    assert not cycling

def test_chemins_non_disjoints():
    with raises(ValueError):
        PathSet([('a', 'b'), ('b', 'c')])


def test_complex_pathset_extension():
    complex_pathset = PathSet(complex_paths)

    res, cycling = complex_pathset.add((complex_paths[0][0], complex_paths[-1][-1]))

    assert res.arcs() == {(complex_paths[0][1], complex_paths[-1][0])} | frozenset(complex_paths[1:-1])
    assert not cycling


def test_complex_pathset_cycle():
    complex_pathset = PathSet(complex_paths)

    res, cycling = complex_pathset.add(complex_paths[-1])

    assert res.arcs() == frozenset(complex_paths[:-1])
    assert cycling
