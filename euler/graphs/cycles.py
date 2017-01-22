from collections import Counter, defaultdict
from functools import reduce
import operator as op


def normalize_path(path):
    return tuple(sorted(path))


class PathSet():
    def __init__(self, paths=None):
        """

        :param paths: an iterable of paths
        """
        self._points = points = {}

        if paths is not None:
            for a, b in paths:
                if a in points or b in points:
                    raise ValueError('les morceaux de chemins ont des points en commun')

                points[a] = b
                points[b] = a

    @classmethod
    def _from_dict(cls, d):
        ps = cls()
        ps._points = d
        return ps

    def add(self, new_path):
        ps, cycling = self.extend([new_path])
        return ps, bool(cycling)

    def extend(self, new_paths):
        """Extend a pathset with an arc

        :param pathset:
        :param arc:
        :return: un tuple qui contient un nouveau pathset et un booléen qui indique si un cycle a été fermé
        """

        points = self._points.copy()
        cycles = 0

        for a, b in new_paths:

            if a in points:
                la = points[a]
                del points[a]
            else:
                la = a
            if b in points:
                lb = points[b]
                del points[b]
            else:
                lb = b

            if la == b:
                cycles += 1
            else:
                points[la] = lb
                points[lb] = la

        return self._from_dict(points), cycles

    def arcs(self):
        return frozenset(normalize_path(path) for path in self._points.items())

    def points(self):
        return frozenset(self._points)

    def __iter__(self):
        return iter(self.arcs())

    def __len__(self):
        return len(self._points) // 2

    def __contains__(self, item):
        a, b = item
        return a in self._points and self._points[a] == b

    def __eq__(self, other):
        return self._points == other._points

    def __hash__(self):
        return hash(self.arcs())

    def __repr__(self):
        return "PathSet({!r})".format(self.arcs())


class WeightSet():
    def __init__(self, w=None):
        if w is None:
            w = []
        self._counter = Counter(w)

    def add_cycles(self, additional_cycles):
        return WeightSet(Counter({n + additional_cycles: w for n, w in self._counter.items()}))

    def __eq__(self, other):
        return self._counter == other._counter

    def __add__(self, other):
        return WeightSet(self._counter + other._counter)

    def __hash__(self):
        return hash(self._counter)

    def __repr__(self):
        return "WeightSet(%r)" % (dict(self._counter),)

    def __iter__(self):
        return iter(self._counter)

    def values(self):
        return self._counter.values()

    def keys(self):
        return self._counter.values()

    def items(self):
        return self._counter.items()


class PartialSolution():
    def __init__(self, pathset, single_points):
        self._pathset = pathset
        self._single_points = frozenset(single_points)

    def extend_single_points(self, forward_arcs):
        current = self._pathset
        single_points = self._single_points
        reached = []

        for sp in single_points:
            neighbours = forward_arcs[sp]
            if len(neighbours) != 2:
                return None, None

            current, cycling = current.add(neighbours)
            reached.extend(neighbours)

            if cycling:
                raise ValueError('Etendre les points isolés ne devrait pas créer de cycle')

        return current, frozenset(reached)

    def successors(self, next_partition, forward_arcs):
        # let's identify the points we'll have to extend
        points = self._pathset.points()
        extended_pathset, points_reached = self.extend_single_points(forward_arcs)

        # Si on ne peut pas étendre les points isolés, pas de possibilités
        if extended_pathset is not None:
            yield from self._successors(points, extended_pathset, 0,
                                        frozenset(next_partition) - points_reached,
                                        forward_arcs)

    def _successors(self, points, extended_pathset, additional_cycles, unreachead_points, forward_arcs):
        if not points:
            yield PartialSolution(extended_pathset, unreachead_points), additional_cycles
            return

        point, *other_points = points

        for neighbour in forward_arcs[point]:
            new_pathset, cycling = extended_pathset.add((point, neighbour))
            yield from self._successors(other_points, new_pathset, additional_cycles + int(cycling),
                                        unreachead_points - {neighbour}, forward_arcs)

    def __eq__(self, other):
        return self._pathset == other._pathset and self._single_points == other._single_points

    def __hash__(self):
        return hash((self._pathset, self._single_points))

    def __repr__(self):
        return "PartialSolution({!r}, {!r})".format(self._pathset, self._single_points)


class PartialSolutionSet():
    """Un ensemble de solutions partielles

    Chaque solution partielle associe un pathset, un ensemble de points isolés et des poids correspondants
    """

    def __init__(self, solution_dict):
        self._solution_dict = dict(solution_dict)

    def extend(self, next_partition, forward_arcs):
        """Renvoie

        :param next_partition:
        :param forward_arcs:
        :return:
        """

        res = defaultdict(WeightSet)

        for partial_solution, weights in self._solution_dict.items():
            for new_solution, additional_cycles in partial_solution.successors(next_partition, forward_arcs):
                res[new_solution] += weights.add_cycles(additional_cycles)

        return PartialSolutionSet(res)

    def __eq__(self, other):
        return self._solution_dict == other._solution_dict

    def __hash__(self):
        return hash(frozenset(self._solution_dict.items()))

    def __repr__(self):
        return "PartialSolutionSet(%r)" % (self._solution_dict,)

    def cumulated_weight(self):
        return reduce(op.add, self._solution_dict.values())


class Problem():
    """Un problème de résolution de cycles

    Contraintes à respecter :
    * le graphe doit déjà avoir été partitionné
    * l'algorithme actuel ne gère que les cas où les noeuds n'ont au maximum que deux voisins en avant
      (dans la partition suivante)

    """

    def __init__(self, partitions, forward_arcs):
        self._partitions = partitions
        self._forward_arcs = forward_arcs
        self._computed = None

    def _compute_solution(self):
        if self._computed is None:
            start_state = PartialSolutionSet({
                PartialSolution(PathSet([]), self._partitions[0]): WeightSet({0: 1})
            })

            self._computed = [start_state]

            current = start_state

            for next_partition in self._partitions[1:]:
                current = current.extend(next_partition, self._forward_arcs)
                self._computed.append(current)

    def full_results(self):
        self._compute_solution()
        return self._computed

    def results(self):
        self._compute_solution()
        return self._computed[-1]

    def main_weight(self):
        self._compute_solution()
        return self._computed[-1]._solution_dict[PartialSolution(PathSet(), {})]

    def num_permutations(self):
        self._compute_solution()
        return sum(w * 2**nc for nc, w in self.main_weight().items())
