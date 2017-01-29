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

    return rectangular_grid(n, n)


def rectangular_grid(m, n):
    if m <= 0 or n <= 0:
        raise ValueError("la taille de la grille doit être strictement positive")

    partitions = [frozenset(code(i-j, j) for j in range(max(0, i-m+1), min(i+1, n))) for i in range(m+n - 1)]
    forward_arcs = {code(i, j): [code(i+1, j), code(i, j+1)] for i in range(m-1) for j in range(n-1)}
    for i in range(m-1):
        forward_arcs[code(i, n-1)] = [code(i+1, n-1)]
    for j in range(n-1):
        forward_arcs[code(m-1, j)] = [code(m-1, j+1)]
    forward_arcs[code(m-1, n-1)] = []

    return partitions, forward_arcs
