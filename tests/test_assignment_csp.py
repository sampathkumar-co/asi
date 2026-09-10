import unittest

from seed.tools.builtin import default_registry


class AssignmentCSPTests(unittest.TestCase):
    def test_logic_grid_solves_and_renders_aliases(self):
        result = default_registry().call(
            "assignment_csp",
            {
                "groups": {
                    "people": ["Alex", "Bea", "Chen", "Dev"],
                    "topics": ["AI", "Databases", "Networks", "Operating Systems"],
                },
                "positions": [1, 2, 3, 4],
                "constraints": [
                    {"op": "position_eq", "entity": "Chen", "position": 4},
                    {"op": "position_eq", "entity": "Databases", "position": 1},
                    {"op": "after", "left": "Alex", "right": "Dev"},
                    {"op": "immediately_before", "left": "AI", "right": "Alex"},
                    {"op": "not_same", "left": "Bea", "right": "AI"},
                    {"op": "not_same", "left": "Bea", "right": "Operating Systems"},
                    {"op": "not_same", "left": "Dev", "right": "Networks"},
                    {"op": "same_position", "left": "Chen", "right": "Networks"},
                ],
                "labels": {"Databases": "DB", "Operating Systems": "OS"},
                "render_groups": [
                    {"name": "people", "group": "people"},
                    {"name": "topics", "group": "topics"},
                ],
                "answer_template": "FINAL: {people} | {topics}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: Bea-Dev-Alex-Chen | DB-AI-OS-Networks")
        self.assertTrue(all(result.output["checks"].values()))

    def test_nonunique_assignment_rejected(self):
        result = default_registry().call(
            "assignment_csp",
            {
                "groups": {"people": ["A", "B"]},
                "positions": [1, 2],
                "constraints": [],
                "render_groups": [{"name": "people", "group": "people"}],
                "answer_template": "FINAL: {people}",
            },
        )
        self.assertFalse(result.ok)
        self.assertIn("not unique", result.error)


if __name__ == "__main__":
    unittest.main()
