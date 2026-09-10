import unittest

from seed.agent.tool_routing import select_tools
from seed.tools.graph import dag_longest_path_tool
from seed.tools.subset_optimize import subset_optimize

AVAILABLE = (
    "calculator", "crt", "dag_longest_path", "python_compute", "python_trace",
    "shortest_path", "subset_optimize", "transaction_ledger", "assignment_csp",
)


class Gate1V5ReliabilityTests(unittest.TestCase):
    def test_cheapest_directed_route_uses_exact_tool_only(self):
        tools = select_tools(
            "Find the unique cheapest directed route from A to Z. Weighted links: A->B 4, B->Z 3.", AVAILABLE
        )
        self.assertIn("shortest_path", tools)
        self.assertNotIn("python_compute", tools)

    def test_hyphenated_project_duration_routes_dag_only(self):
        tools = select_tools(
            "Project durations A4,B5,C6. C after A. Unlimited workers. Return the critical-path.", AVAILABLE
        )
        self.assertIn("dag_longest_path", tools)
        self.assertNotIn("python_compute", tools)
    def test_python_trace_specialization_hides_python_compute(self):
        tools = select_tools(
            "Trace this Python exactly: def f(x): return x+1\nprint(f(2))", AVAILABLE
        )
        self.assertIn("python_trace", tools)
        self.assertNotIn("python_compute", tools)

    def test_dag_duration_suffixes_render_bare_task_ids(self):
        result = dag_longest_path_tool({
            "weights": {"J6": 6, "L4": 4, "O5": 5, "P4": 4, "R6": 6},
            "predecessors": {"J6": [], "L4": ["J6"], "O5": ["L4"], "P4": ["O5"], "R6": ["P4"]},
            "answer_template": "FINAL: {weight} | {path}", "path_separator": "-",
        })
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: 25 | J-L-O-P-R")

    def test_subset_single_letter_whitespace_separator_is_canonicalized(self):
        result = subset_optimize({
            "items": [{"name":"B","weight":3,"value":9},{"name":"E","weight":6,"value":18},
                      {"name":"G","weight":4,"value":13},{"name":"H","weight":2,"value":7}],
            "capacity": 15, "constraints": {"implies": [["H","B"]], "exclusive": []},
            "answer_template": "FINAL: {value} | {items}", "item_separator": " ",
        })
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: 47 | BEGH")

    def test_dag_mixed_suffix_weights_and_bare_predecessors(self):
        result = dag_longest_path_tool({
            "weights": {"J6":6,"K3":3,"L4":4,"M7":7,"N2":2,"O5":5,"P4":4,"Q3":3,"R6":6},
            "predecessors": {"L":["J"],"M":["K"],"N":["L","M"],"O":["L"],"P":["N","O"],"Q":["M"],"R":["P","Q"]},
            "answer_template": "FINAL: {weight} | {path}", "path_separator": "-",
        })
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: 25 | J-L-O-P-R")


if __name__ == "__main__":
    unittest.main()
