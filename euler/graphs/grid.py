import networkx as nx

__all__ = ['Graph']


def square_grid(n):
    """
    Return a square_grid and a partition
    :param n:
    :return:
    """

    n = int(n)

    if n <= 0:
        raise ValueError("n doit être strictement positif")

    partitions = [frozenset((j, i-j) for j in range(max(0, i-n+1), min(i+1, n))) for i in range(2*n-1)]
    forward_arcs = {(i, j): [(i+1, j), (i, j+1)] for i in range(n-1) for j in range(n-1)}
    for i in range(n-1):
        forward_arcs[(i, n-1)] = [(i+1, n-1)]
        forward_arcs[(n-1, i)] = [(n-1, i+1)]
    forward_arcs[(n-1, n-1)] = []

    return partitions, forward_arcs
