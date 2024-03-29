################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
import copy

import pytest
from orquestra.quantum.operators import PauliTerm

from orquestra.opt.problems import MaxCut

from ._helpers import make_graph

MONOTONIC_GRAPH_OPERATOR_TERM_PAIRS = [
    (
        make_graph(node_ids=range(2), edges=[(0, 1)]),
        [PauliTerm("I0", -0.5), PauliTerm({0: "Z", 1: "Z"}, 0.5)],
    ),
    (
        make_graph(node_ids=range(3), edges=[(0, 1), (0, 2)]),
        [
            PauliTerm("I0", -1),
            PauliTerm({0: "Z", 1: "Z"}, 0.5),
            PauliTerm({0: "Z", 2: "Z"}, 0.5),
        ],
    ),
    (
        make_graph(
            node_ids=range(4), edges=[(0, 1, 1), (0, 2, 2), (0, 3, 3)], use_weights=True
        ),
        [
            PauliTerm("I0", -3),
            PauliTerm({0: "Z", 1: "Z"}, 0.5),
            PauliTerm({0: "Z", 2: "Z"}, 1),
            PauliTerm({0: "Z", 3: "Z"}, 1.5),
        ],
    ),
    (
        make_graph(node_ids=range(5), edges=[(0, 1), (1, 2), (3, 4)]),
        [
            PauliTerm("I0", -1.5),
            PauliTerm({0: "Z", 1: "Z"}, 0.5),
            PauliTerm({1: "Z", 2: "Z"}, 0.5),
            PauliTerm({3: "Z", 4: "Z"}, 0.5),
        ],
    ),
]

GRAPH_OPERATOR_TERM_SCALING_OFFSET_LIST = [
    (
        make_graph(
            node_ids=range(4),
            edges=[(0, 1, 1), (0, 2, 2), (0, 3, 3)],
            use_weights=True,
        ),
        [
            PauliTerm("I0", 1),
            PauliTerm({0: "Z", 1: "Z"}, 1),
            PauliTerm({0: "Z", 2: "Z"}, 2),
            PauliTerm({0: "Z", 3: "Z"}, 3),
        ],
        2.0,
        7.0,
    ),
]

NONMONOTONIC_GRAPH_OPERATOR_TERM_PAIRS = [
    (
        make_graph(node_ids=[4, 2], edges=[(2, 4)]),
        [PauliTerm("I0", -0.5), PauliTerm({0: "Z", 1: "Z"}, 0.5)],
    ),
    (
        make_graph(node_ids="CBA", edges=[("C", "B"), ("C", "A")]),
        [
            PauliTerm("I0", -1),
            PauliTerm({0: "Z", 1: "Z"}, 0.5),  # the C-B edge
            PauliTerm({0: "Z", 2: "Z"}, 0.5),  # the C-A edge
        ],
    ),
]

GRAPH_SOLUTION_COST_LIST = [
    (make_graph(node_ids=range(2), edges=[(0, 1)]), (0, 0), 0),
    (make_graph(node_ids=range(2), edges=[(0, 1)]), (0, 1), -1),
    (
        make_graph(
            node_ids=range(4), edges=[(0, 1, 1), (0, 2, 2), (0, 3, 3)], use_weights=True
        ),
        (1, 0, 0, 0),
        -6,
    ),
    (make_graph(node_ids=range(4), edges=[(0, 1), (0, 2), (0, 3)]), (0, 0, 1, 1), -2),
    (make_graph(node_ids=range(4), edges=[(0, 1), (0, 2), (0, 3)]), (0, 1, 1, 1), -3),
    (
        make_graph(node_ids=range(5), edges=[(0, 1), (1, 2), (3, 4)]),
        (1, 1, 1, 1, 1),
        0,
    ),
]

GRAPH_BEST_SOLUTIONS_COST_LIST = [
    (make_graph(node_ids=range(2), edges=[(0, 1)]), [(0, 1), (1, 0)], -1),
    (
        make_graph(node_ids=range(3), edges=[(0, 1), (0, 2)]),
        [(0, 1, 1), (1, 0, 0)],
        -2,
    ),
    (
        make_graph(node_ids=range(4), edges=[(0, 1), (0, 2), (0, 3)]),
        [
            (0, 1, 1, 1),
            (1, 0, 0, 0),
        ],
        -3,
    ),
    (
        make_graph(node_ids=range(5), edges=[(0, 1), (1, 2), (3, 4)]),
        [(0, 1, 0, 0, 1), (0, 1, 0, 1, 0), (1, 0, 1, 0, 1), (1, 0, 1, 1, 0)],
        -3,
    ),
]


class TestGetMaxcutHamiltonian:
    @pytest.mark.parametrize(
        "graph,terms",
        [
            *MONOTONIC_GRAPH_OPERATOR_TERM_PAIRS,
            *NONMONOTONIC_GRAPH_OPERATOR_TERM_PAIRS,
        ],
    )
    def test_returns_expected_terms(self, graph, terms):
        pauli_sum = MaxCut().get_hamiltonian(graph)
        assert set(pauli_sum.terms) == set(terms)

    @pytest.mark.parametrize(
        "graph,terms,scale_factor,offset",
        [*GRAPH_OPERATOR_TERM_SCALING_OFFSET_LIST],
    )
    def test_scaling_and_offset_works(self, graph, terms, scale_factor, offset):
        pauli_sum = MaxCut().get_hamiltonian(graph, scale_factor, offset)
        assert set(pauli_sum.terms) == set(terms)


class TestEvaluateMaxcutSolution:
    @pytest.mark.parametrize("graph,solution,target_value", [*GRAPH_SOLUTION_COST_LIST])
    def test_evaluate_maxcut_solution(self, graph, solution, target_value):
        value = MaxCut().evaluate_solution(solution, graph)
        assert value == target_value

    @pytest.mark.parametrize("graph,solution,target_value", [*GRAPH_SOLUTION_COST_LIST])
    def test_evaluate_maxcut_solution_with_invalid_input(
        self, graph, solution, target_value
    ):
        too_long_solution = solution + (1,)
        too_short_solution = solution[:-1]
        invalid_value_solution = copy.copy(solution)
        invalid_value_solution = list(invalid_value_solution)
        invalid_value_solution[0] = -1
        invalid_value_solution = tuple(invalid_value_solution)
        invalid_solutions = [
            too_long_solution,
            too_short_solution,
            invalid_value_solution,
        ]
        for invalid_solution in invalid_solutions:
            with pytest.raises(ValueError):
                _ = MaxCut().evaluate_solution(invalid_solution, graph)


class TestSolveMaxcutByExhaustiveSearch:
    @pytest.mark.parametrize(
        "graph,target_solutions,target_value", [*GRAPH_BEST_SOLUTIONS_COST_LIST]
    )
    def test_solve_maxcut_by_exhaustive_search(
        self, graph, target_solutions, target_value
    ):
        value, solutions = MaxCut().solve_by_exhaustive_search(graph)
        assert set(solutions) == set(target_solutions)
        assert value == target_value
