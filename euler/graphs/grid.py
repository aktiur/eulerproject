__all__ = ['square_grid']

letters = "abcdefghijklmnopqrstuvwxyz"

def code(ligne, colonne):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    ligne += 1
    while ligne:
        ligne, rem = divmod(ligne - 1, 26)
        result[:0] = letters[rem]
    return ''.join(result) + str(colonne)

def square_grid(n):
    """
    Return a square_grid and a partition
    :param n:
    :return:
    """

    n = int(n)

    if n <= 0:
        raise ValueError("n doit être strictement positif")

    partitions = [frozenset(code(j, i-j) for j in range(max(0, i-n+1), min(i+1, n))) for i in range(2*n-1)]
    forward_arcs = {code(i, j): [code(i+1, j), code(i, j+1)] for i in range(n-1) for j in range(n-1)}
    for i in range(n-1):
        forward_arcs[code(i, n-1)] = [code(i+1, n-1)]
        forward_arcs[code(n-1, i)] = [code(n-1, i+1)]
    forward_arcs[code(n-1, n-1)] = []

    return partitions, forward_arcs
