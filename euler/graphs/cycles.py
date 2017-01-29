from collections import Counter, defaultdict
from functools import reduce
from itertools import product
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


class WeightSet(Counter):
    def add_cycles(self, additional_cycles):
        return WeightSet(Counter({n + additional_cycles: w for n, w in self.items()}))


class PartialSolution():
    def __init__(self, pathset, single_points):
        self._pathset = pathset
        self._single_points = frozenset(single_points)

    def extend_single_points(self, forward_arcs):
        neighbours_list = [forward_arcs[sp] for sp in self._single_points]
        if any(len(neighbours) != 2 for neighbours in neighbours_list):
            return None, None

        new_pathset, cycles = self._pathset.extend(neighbours_list)

        if cycles:
            raise ValueError('Etendre les points isolés ne devrait pas créer de cycle')

        return new_pathset, frozenset(point for path in neighbours_list for point in path)

    def successors(self, next_partition, forward_arcs):
        # let's identify the points we'll have to extend
        points = self._pathset.points()
        extended_pathset, points_reached = self.extend_single_points(forward_arcs)

        if extended_pathset is None:
            # pas de possibilité d'étendre les points isolés, on s'arrête là
            return

        points_left = frozenset(next_partition) - points_reached
        assignments = (tuple((p, n) for n in forward_arcs[p]) for p in points)

        for new_paths in product(*assignments):
            new_pathset, additional_cycles = extended_pathset.extend(new_paths)
            yield PartialSolution(new_pathset, points_left - frozenset(n for p,n in new_paths)), additional_cycles

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

    def weights(self):
        self._compute_solution()
        return self._computed[-1]._solution_dict[PartialSolution(PathSet(), {})]

    def num_solutions(self):
        return sum(w * 2**nc for nc, w in self.weights().items())

    def num_hamiltonian_cycles(self):
        return self.weights()[1]

    def num_2_factors(self):
        return sum(self.weights().values())
