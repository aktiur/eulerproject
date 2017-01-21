from . import grid

def test_grid_size():
    for m in range(1,11):
        partitions, forward_arcs = grid.square_grid(m)
        assert len(partitions) == 2*m-1
        assert len(forward_arcs) == m*m

letters = 'abcdefghijklmnopqrstuvwxyz'

def test_extreme_partitions():
    for m in range(1,11):
        partitions, _ = grid.square_grid(m)
        assert partitions[0] == {('a0')}
        assert partitions[-1] == {letters[m-1] + str(m-1)}

def test_4_partitions():
    partitions, forward_arcs = grid.square_grid(4)

    assert partitions[0] == {'a0'}
    assert partitions[1] == {'a1', 'b0'}
    assert partitions[2] == {'a2', 'b1', 'c0'}
    assert partitions[3] == {'a3', 'b2', 'c1', 'd0'}
    assert partitions[4] == {'b3', 'c2', 'd1'}
    assert partitions[5] == {'c3', 'd2'}
    assert partitions[6] == {'d3'}

def test_arcs_between_consecutive_parts():
    for m in range(1,11):
        partitions, forward_arcs = grid.square_grid(m)

        for i in range(len(partitions) - 1):
            for origin in partitions[i]:
                for destination in forward_arcs[origin]:
                    assert destination in partitions[i+1], "l'arc ne va pas d'une partition à la suivante"
