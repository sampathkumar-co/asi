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

    def test_unknown_tool_denied(self):
        result = default_registry().call("shell", {"command": "whoami"})
        self.assertFalse(result.ok)
        self.assertIn("not allowed", result.error)


if __name__ == "__main__":
    unittest.main()
