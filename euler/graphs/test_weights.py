from .cycles import WeightSet

simple_weighset = WeightSet({1: 2, 2: 1, 3:1})


def test_ajouter_cycles():
    assert simple_weighset.add_cycles(1) == WeightSet({2:2, 3:1, 4:1})


def test_ajouter_poids():
    assert simple_weighset + WeightSet({2:2, 4:1}) == WeightSet({1:2, 2:3, 3:1, 4:1})
