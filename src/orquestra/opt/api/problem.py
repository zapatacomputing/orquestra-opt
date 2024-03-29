################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
from abc import ABC, abstractmethod
from typing import List, Tuple

import networkx as nx
from orquestra.quantum.operators import PauliSum

from ._problem_evaluation import (
    evaluate_solution,
    solve_graph_problem_by_exhaustive_search,
)


class Problem(ABC):
    @abstractmethod
    def _build_hamiltonian(self, graph: nx.Graph) -> PauliSum:
        """
        This abstract method is implemented by the subclasses, and
        its goal is to encode the graph of the problem in the form
        of qubit operator.
        """

    def get_hamiltonian(
        self, graph: nx.Graph, scale_factor: float = 1.0, offset: float = 0.0
    ) -> PauliSum:
        # Relabeling for monotonicity purposes
        num_nodes = range(len(graph.nodes))
        mapping = {node: new_label for node, new_label in zip(graph.nodes, num_nodes)}
        graph = nx.relabel_nodes(graph, mapping=mapping)

        hamiltonian = self._build_hamiltonian(graph)

        return hamiltonian * scale_factor + offset

    def evaluate_solution(self, solution: Tuple[int], graph: nx.Graph) -> float:
        return evaluate_solution(solution, graph, self.get_hamiltonian)

    def solve_by_exhaustive_search(
        self,
        graph: nx.Graph,
    ) -> Tuple[float, List[Tuple[int, ...]]]:
        return solve_graph_problem_by_exhaustive_search(
            graph, cost_function=self.evaluate_solution
        )
