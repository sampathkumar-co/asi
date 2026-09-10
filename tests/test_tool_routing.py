import unittest

from seed.agent.tool_routing import select_tools


AVAILABLE = (
    "aggregate_records",
    "assignment_csp",
    "calculator",
    "crt",
    "dag_longest_path",
    "echo",
    "finite_csp",
    "python_compute",
    "shortest_path",
    "subset_optimize",
    "transaction_ledger",
    "python_trace",
)


class ToolRoutingTests(unittest.TestCase):
    def test_shortest_path_routes_exact_graph_tool(self):
        tools = select_tools("Find the unique shortest path from S to T using weighted directed edges.", AVAILABLE)
        self.assertIn("shortest_path", tools)
        self.assertNotIn("python_compute", tools)
        self.assertNotIn("crt", tools)

    def test_shortest_route_paraphrases_route_exact_graph_tool(self):
        cases = (
            "Find the unique minimum-cost directed route from S to T. Weighted arcs: S->A 6, A->T 2.",
            "A one-way network has edges P->Q=5, Q->Z=3. Determine the unique shortest P-to-Z path.",
        )
        for prompt in cases:
            with self.subTest(prompt=prompt):
                self.assertIn("shortest_path", select_tools(prompt, AVAILABLE))

    def test_project_schedule_routes_dag_tool(self):
        tools = select_tools("Find the critical path and project completion time with prerequisites.", AVAILABLE)
        self.assertIn("dag_longest_path", tools)
        self.assertNotIn("shortest_path", tools)

    def test_congruences_route_crt(self):
        tools = select_tools("Find n where n ≡ 2 mod 5 and n ≡ 3 mod 7.", AVAILABLE)
        self.assertIn("crt", tools)
        self.assertNotIn("aggregate_records", tools)

    def test_ledger_routes_semantic_transaction_tool(self):
        tools = select_tools("Only POSTED ledger records count; sales, refund and fee records follow.", AVAILABLE)
        self.assertIn("transaction_ledger", tools)
        self.assertNotIn("aggregate_records", tools)
        self.assertNotIn("dag_longest_path", tools)

    def test_logic_grid_routes_assignment_csp(self):
        tools = select_tools("Four researchers present once each Monday through Thursday, each a different topic. Determine the unique day order.", AVAILABLE)
        self.assertIn("assignment_csp", tools)
        self.assertNotIn("python_compute", tools)
        self.assertNotIn("finite_csp", tools)

    def test_position_order_routes_assignment_csp(self):
        tools = select_tools("Seven jobs must be arranged in positions 1-7. Exactly two positions lie between G and C.", AVAILABLE)
        self.assertIn("assignment_csp", tools)

    def test_subset_optimization_routes_exact_tool(self):
        tools = select_tools("Items have weight and value; choose a subset maximizing total value under capacity and logical constraints.", AVAILABLE)
        self.assertIn("subset_optimize", tools)
        self.assertNotIn("python_compute", tools)


if __name__ == "__main__":
    unittest.main()
