from .cycles import Problem
from .grid import square_grid

def test_problem_4():
    p = Problem(*square_grid(4))

    assert p.num_solutions() == 88
    assert p.num_hamiltonian_cycles() == 6
    assert p.num_2_factors() == 18


def test_problem_6():
    p = Problem(*square_grid(6))

    assert p.num_hamiltonian_cycles() == 1072
    assert p.num_2_factors() == 13903


def test_problem_8():
    p = Problem(*square_grid(8))

    assert p.num_hamiltonian_cycles() == 4638576
    assert p.num_2_factors() == 360783593
