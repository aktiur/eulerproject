from collections import Counter
from itertools import chain


def normalize_path(path):
    return tuple(sorted(path))


def combine_paths(path1, path2):
    if path1[0] == path2[0]:
        path = (path1[1], path2[1])
    elif path1[0] == path2[1]:
        path = (path1[1], path2[0])
    elif path1[1] == path2[0]:
        path = (path1[0], path2[1])
    elif path1[1] == path2[1]:
        path = (path1[0], path2[0])
    else:
        raise ValueError('arcs not combinable')

    return normalize_path(path)


class PathSet():
    def __init__(self, paths=None):
        """

        :param paths: an iterable of paths
        :param isolated_points: an iterable of points
        :param weights: a counter of weights (for every number of cycles)
        """
        self._paths = paths = frozenset(normalize_path(path) for path in paths)

        self._points = points = {}

        for a, b in paths:
            if a in points or b in points:
                raise ValueError('les morceaux de chemins ont des points en commun')

            points[a] = (a, b)
            points[b] = (a, b)

    def extend(self, new_path):
        """Extend a pathset with an arc

        :param pathset:
        :param arc:
        :return: un tuple qui contient un nouveau pathset et un booléen qui indique si un cycle a été fermé
        """

        paths = self._paths
        points = self._points
        new_path = normalize_path(new_path)

        connected = frozenset(points[i] for i in new_path if i in points)

        cycling = False
        res = []

        for path in connected:
            if path == new_path:
                new_path = None
                cycling = True
            else:
                new_path = combine_paths(path, new_path)

        res = paths - connected
        if new_path:
            res |= {new_path}

        return PathSet(res), cycling

    def arcs(self):
        return self._paths

    def points(self):
        return frozenset(self._points)

    def __iter__(self):
        return iter(self._paths)

    def __len__(self):
        return len(self._paths)

    def __contains__(self, item):
        return item in self._paths

    def __eq__(self, other):
        return self._paths == other._paths


class WeightSet():
    def __init__(self, w=None):
        if w is None:
            w = []
        self._counter = Counter(w)


class PartialSolution():
    def __init__(self, pathset, single_points):
        self._pathset = pathset
        self._single_points = frozenset(single_points)

    def extend_single_points(self, forward_arcs):
        current = self._pathset
        single_points = self._single_points

        for sp in single_points:
            if len(forward_arcs[sp]) != 2:
                return None
            current, cycling = current.extend(forward_arcs[sp])

            if cycling:
                raise ValueError('Etendre les points isolés ne devrait pas créer de cycle')

        return current

    def successors(self, next_partition, forward_arcs):
        extended_pathset = self.extend_single_points(forward_arcs)

        # Si on ne peut pas étendre les points isolés, pas de possibilités
        if extended_pathset is None:
            return

        points = extended_pathset.points()

        yield from self._successors(points, extended_pathset, 0, next_partition, forward_arcs)

    def _successors(self, points, extended_pathset, additional_cycles, next_partition, forward_arcs):
        if not points:
            yield PartialSolution(extended_pathset, next_partition - extended_pathset.points()), additional_cycles
            return

        point, *other_points = points

        for neighbour in forward_arcs[point]:
            new_pathset, cycling = extended_pathset.extend((point, neighbour))
            yield from self._successors(other_points, new_pathset, additional_cycles + int(cycling), next_partition,
                                        forward_arcs)

    def __eq__(self, other):
        return self._pathset == other._pathset and self._single_points == other._single_points


class PartialSolutionSet():
    """Un ensemble de solutions partielles

    Chaque solution partielle associe un pathset, un ensemble de points isolés et des poids correspondants
    """

    def __init__(self, partial_solutions=None):
        pass

    def extend(self, next_partition, forward_arcs):
        """Renvoie

        :param next_partition:
        :param forward_arcs:
        :return:
        """

    def __iter__(self):
        """Itérateur qui renvoie les éléments de solution

        :return:
        """
        if False:
            yield PartialSolutionSet()