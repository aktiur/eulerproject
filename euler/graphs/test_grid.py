from . import grid

def test_grid_size():
    for m in range(1,11):
        partitions, forward_arcs = grid.square_grid(m)
        assert len(partitions) == 2*m-1
        assert len(forward_arcs) == m*m

def test_extreme_partitions():
    for m in range(1,11):
        partitions, _ = grid.square_grid(m)
        assert partitions[0] == {(0,0)}
        assert partitions[-1] == {(m-1, m-1)}

def test_4_partitions():
    partitions, forward_arcs = grid.square_grid(4)

    assert partitions[0] == {(0,0)}
    assert partitions[1] == {(0,1), (1,0)}
    assert partitions[2] == {(0,2), (1,1), (2,0)}
    assert partitions[3] == {(0,3), (1,2), (2,1), (3,0)}
    assert partitions[4] == {(1,3), (2,2), (3,1)}
    assert partitions[5] == {(2,3), (3,2)}
    assert partitions[6] == {(3,3)}

def test_arcs_between_consecutive_parts():
    for m in range(1,11):
        partitions, forward_arcs = grid.square_grid(m)

        for i in range(len(partitions) - 1):
            for origin in partitions[i]:
                for destination in forward_arcs[origin]:
                    assert destination in partitions[i+1], "l'arc ne va pas d'une partition à la suivante"
