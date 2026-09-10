import unittest

from seed.agent.tool_routing import select_tools


AVAILABLE = (
    "aggregate_records",
    "calculator",
    "crt",
    "dag_longest_path",
    "echo",
    "python_compute",
    "shortest_path",
)


class ToolRoutingTests(unittest.TestCase):
    def test_shortest_path_routes_exact_graph_tool(self):
        tools = select_tools("Find the unique shortest path from S to T using weighted directed edges.", AVAILABLE)
        self.assertIn("shortest_path", tools)
        self.assertIn("python_compute", tools)
        self.assertNotIn("crt", tools)

    def test_project_schedule_routes_dag_tool(self):
        tools = select_tools("Find the critical path and project completion time with prerequisites.", AVAILABLE)
        self.assertIn("dag_longest_path", tools)
        self.assertNotIn("shortest_path", tools)

    def test_congruences_route_crt(self):
        tools = select_tools("Find n where n ≡ 2 mod 5 and n ≡ 3 mod 7.", AVAILABLE)
        self.assertIn("crt", tools)
        self.assertNotIn("aggregate_records", tools)

    def test_ledger_routes_aggregation(self):
        tools = select_tools("Only POSTED ledger records count; sales, refund and fee records follow.", AVAILABLE)
        self.assertIn("aggregate_records", tools)
        self.assertNotIn("dag_longest_path", tools)

    def test_generic_constraint_task_keeps_small_fallback_set(self):
        tools = select_tools("Arrange seven jobs subject to ordering constraints.", AVAILABLE)
        self.assertEqual(tools, ("calculator", "python_compute"))


if __name__ == "__main__":
    unittest.main()
