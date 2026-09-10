import unittest
from seed.tools.builtin import calculator, default_registry


class ToolTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculator({"expression": "2 + 3*4"}).output, 14)

    def test_calculator_rejects_code(self):
        result = calculator({"expression": "__import__('os').system('echo bad')"})
        self.assertFalse(result.ok)

    def test_dag_longest_path_tool_returns_verified_answer(self):
        result = default_registry().call(
            "dag_longest_path",
            {
                "weights": {"S": 2, "A": 4, "B": 3, "T": 5},
                "predecessors": {"S": [], "A": ["S"], "B": ["S"], "T": ["A", "B"]},
                "target": "T",
                "answer_template": "FINAL: {weight} | {path}",
                "path_separator": "-",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: 11 | S-A-T")
        self.assertTrue(all(result.output["checks"].values()))

    def test_dag_longest_path_tool_rejects_cycle(self):
        result = default_registry().call(
            "dag_longest_path",
            {
                "weights": {"A": 1, "B": 2},
                "predecessors": {"A": ["B"], "B": ["A"]},
                "target": "B",
                "answer_template": "FINAL: {weight} | {path}",
            },
        )
        self.assertFalse(result.ok)
        self.assertIn("acyclic", result.error)

    def test_shortest_path_tool_returns_unique_verified_path(self):
        result = default_registry().call(
            "shortest_path",
            {
                "edges": [["S", "A", 5], ["S", "B", 2], ["B", "A", 1], ["A", "T", 3], ["B", "T", 9]],
                "source": "S",
                "target": "T",
                "answer_template": "FINAL: {cost} | {path}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: 6 | S-B-A-T")
        self.assertTrue(all(result.output["checks"].values()))

    def test_crt_tool_returns_smallest_positive_solution(self):
        result = default_registry().call(
            "crt",
            {"congruences": [[1, 4], [3, 5], [2, 7]], "answer_template": "FINAL: {solution}"},
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: 93")
        self.assertTrue(all(result.output["checks"].values()))

    def test_aggregate_records_filters_and_sums_exactly(self):
        result = default_registry().call(
            "aggregate_records",
            {
                "records": [
                    {"group": "A", "status": "POSTED", "sign": "add", "factors": [2, 50], "discount_percent": 10},
                    {"group": "A", "status": "VOID", "sign": "subtract", "amount": 99},
                    {"group": "B", "status": "POSTED", "sign": "subtract", "amount": 5.5},
                ],
                "include_statuses": ["POSTED"],
                "decimal_places": 2,
                "answer_template": "FINAL: A={A},B={B},TOTAL={TOTAL}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: A=90.00,B=-5.50,TOTAL=84.50")
        self.assertTrue(all(result.output["checks"].values()))

    def test_finite_csp_solves_unique_logic_grid(self):
        positions = [1, 2, 3, 4]
        result = default_registry().call(
            "finite_csp",
            {
                "domains": {name: positions for name in ["Alex", "Bea", "Chen", "Dev", "DB", "AI", "OS", "Networks"]},
                "all_different": [["Alex", "Bea", "Chen", "Dev"], ["DB", "AI", "OS", "Networks"]],
                "constraints": [
                    {"op": "eq", "left": "Chen", "value": 4},
                    {"op": "eq", "left": "DB", "value": 1},
                    {"op": "gt", "left": "Alex", "right": "Dev"},
                    {"op": "offset_eq", "left": "Alex", "right": "AI", "value": 1},
                    {"op": "ne", "left": "Bea", "right": "AI"},
                    {"op": "ne", "left": "Bea", "right": "OS"},
                    {"op": "ne", "left": "Dev", "right": "Networks"},
                    {"op": "eq", "left": "Chen", "right": "Networks"},
                ],
                "sequences": [
                    {"name": "people", "variables": ["Alex", "Bea", "Chen", "Dev"], "order": positions},
                    {"name": "topics", "variables": ["DB", "AI", "OS", "Networks"], "order": positions},
                ],
                "answer_template": "FINAL: {people} | {topics}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: Bea-Dev-Alex-Chen | DB-AI-OS-Networks")
        self.assertTrue(all(result.output["checks"].values()))

    def test_finite_csp_rejects_nonunique_problem(self):
        result = default_registry().call(
            "finite_csp",
            {
                "domains": {"A": [1, 2], "B": [1, 2]},
                "all_different": [["A", "B"]],
                "constraints": [],
                "sequences": [{"name": "order", "variables": ["A", "B"], "order": [1, 2]}],
                "answer_template": "FINAL: {order}",
            },
        )
        self.assertFalse(result.ok)
        self.assertIn("not unique", result.error)

    def test_unknown_tool_denied(self):
        result = default_registry().call("shell", {"command": "whoami"})
        self.assertFalse(result.ok)
        self.assertIn("not allowed", result.error)


if __name__ == "__main__":
    unittest.main()
