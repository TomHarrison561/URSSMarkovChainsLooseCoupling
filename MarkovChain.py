import networkx as nx
import numpy as np
from scipy.optimize import linprog

class PathCoupling:
    def __init__(self, graph: nx.Graph, rho=None):
        self.graph = graph

        self.nodes = list(graph.nodes())
        self.num_nodes = len(self.nodes)

        # trivial case of one node:
        self.max_degree = (
            max(dict(graph.degree()).values()) if self.num_nodes > 0 else 1
        )

        if rho is None:
            # create a dictionary for the normal path metric (shortest path length) between meanders
            self._path_lengths = dict(
                nx.all_pairs_shortest_path_length(self.graph)
            )
            self.rho = self._default_rho
        else:
            self.rho = rho

    def _default_rho(self, u, v) -> float:
        return self._path_lengths[u][v]

    def get_transition_probability(self, u, v) -> float:
        # markov chain as defined in the paper
        if u == v:
            deg_u = self.graph.degree(u)
            return 1.0 - (deg_u / self.max_degree)
        elif self.graph.has_edge(u, v):
            return 1.0 / self.max_degree
        else:
            return 0.0

    def compute_minimal_coupling(self, x, y):
        N = self.num_nodes

        # list representing the marginals
        p_x = np.array([self.get_transition_probability(x, s) for s in self.nodes])
        p_y = np.array([self.get_transition_probability(y, s) for s in self.nodes])

        b_eq = np.concatenate([p_x, p_y])

        # cost vector which we flatten
        c = np.zeros((N, N))    # N by N zero matrix
        for i, s_i in enumerate(self.nodes):
            for j, s_j in enumerate(self.nodes):
                c[i, j] = self.rho(s_i, s_j)
        c_flat = c.flatten()

        A_eq = np.zeros((2 * N, N * N))

        # : means continuous block slice
        for i in range(N):
            A_eq[i, i * N: (i + 1) * N] = 1.0

        # :: is a stride slice
        for j in range(N):
            A_eq[N + j, j::N] = 1.0

        res = linprog(c_flat, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method='highs')   # keep gamma positive with bounds

        if res.success:
            min_expected_distance = res.fun
            optimal_gamma = res.x.reshape((N, N))
            return min_expected_distance, optimal_gamma # optimal gamma not really needed to return
        else:
            raise RuntimeError(f"Linear programming optimization failed for edge ({x}, {y}).")

    def check_all_edges(self):
        worst_case = 0.0
        worst_edge = None

        for x, y in self.graph.edges():
            exp_dist, _ = self.compute_minimal_coupling(x, y)
            if exp_dist > worst_case:
                worst_case = exp_dist
                worst_edge = (x, y)

        # do we want our worst case to be < 1 ?
        return worst_case, worst_edge