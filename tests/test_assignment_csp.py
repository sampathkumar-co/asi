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

    def test_compact_strings_and_render_lists_are_normalized(self):
        result = default_registry().call(
            "assignment_csp",
            {
                "groups": {
                    "people": ["Alex", "Bea", "Chen", "Dev"],
                    "topics": ["AI", "Databases", "Operating Systems", "Networks"],
                },
                "positions": [1, 2, 3, 4],
                "constraints": [
                    "position_eq(Chen,4)",
                    "position_eq(Databases,1)",
                    "after(Alex,Dev)",
                    "immediately_before(AI,Alex)",
                    "not_same(Bea,AI)",
                    "not_same(Bea,Operating Systems)",
                    "not_same(Dev,Networks)",
                    "position_eq(Chen,Networks)",
                ],
                "labels": {"Databases": "DB", "Operating Systems": "OS"},
                "render_groups": [
                    {"name": "people", "group": ["Mon-person", "Tue-person", "Wed-person", "Thu-person"]},
                    {"name": "topics", "group": ["Mon-topic", "Tue-topic", "Wed-topic", "Thu-topic"]},
                ],
                "answer_template": "FINAL: {people} | {topics}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: Bea-Dev-Alex-Chen | DB-AI-OS-Networks")

    def test_not_in_topics_alias_expands_to_not_same_any(self):
        result = default_registry().call(
            "assignment_csp",
            {
                "groups": {
                    "people": ["Alex", "Bea", "Chen", "Dev"],
                    "topics": ["AI", "Databases", "Networks", "Operating Systems"],
                },
                "positions": [1, 2, 3, 4],
                "constraints": [
                    "position_eq(Chen,4)", "position_eq(Databases,1)", "after(Alex,Dev)",
                    "immediately_before(AI,Alex)", "not_in_topics(Bea,[AI, Operating Systems])",
                    "not_in_topics(Dev,[Networks])", "position_eq(Chen,Networks)",
                ],
                "labels": {"Databases": "DB", "Operating Systems": "OS"},
                "render_groups": [{"name": "people", "group": "people"}, {"name": "topics", "group": "topics"}],
                "answer_template": "FINAL: {people} | {topics}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: Bea-Dev-Alex-Chen | DB-AI-OS-Networks")

    def test_positions_between_and_numeric_position_exclusion(self):
        result = default_registry().call(
            "assignment_csp",
            {
                "groups": {"packages": ["G", "H", "I", "J", "K", "L"]},
                "positions": [1, 2, 3, 4, 5, 6],
                "constraints": [
                    "position_eq(J,2)", "immediately_after(K,H)", "before(G,H)",
                    "after(L,K)", "positions_between(I,G,1)", "before(G,I)", "not_same(I,6)",
                ],
                "labels": {},
                "render_groups": [{"name": "packages", "group": "packages"}],
                "answer_template": "FINAL: {packages}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: GJIHKL")
        self.assertTrue(all(result.output["checks"].values()))

    def test_source_clues_rebind_mis_copied_entity_pairs(self):
        result = default_registry().call(
            "assignment_csp",
            {
                "groups": {"people": ["Lina", "Omar", "Priya", "Ravi"], "topics": ["Cloud", "AI", "DB", "OS"]},
                "positions": [1, 2, 3, 4],
                "source_clues": [
                    "Omar speaks Tuesday.", "DB is Thursday.", "Priya speaks later than Lina.",
                    "Lina speaks before Ravi.", "AI is immediately before Priya.",
                    "Ravi is not Cloud.", "Lina is not OS.", "Omar is not AI.",
                ],
                "constraints": [
                    {"op": "position_eq", "entity": "Omar", "position": 2},
                    {"op": "position_eq", "entity": "DB", "position": 4},
                    {"op": "after", "left": "Lina", "right": "Ravi"},
                    {"op": "before", "left": "Ravi", "right": "Priya"},
                    {"op": "immediately_before", "left": "AI", "right": "Priya"},
                    {"op": "not_same", "left": "Ravi", "right": "Cloud"},
                    {"op": "not_same", "left": "Lina", "right": "OS"},
                    {"op": "not_same", "left": "Omar", "right": "AI"},
                ],
                "labels": {},
                "render_groups": [{"name": "people", "group": "people"}, {"name": "topics", "group": "topics"}],
                "answer_template": "FINAL: {people} | {topics}",
            },
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output["answer"], "FINAL: Lina-Omar-Ravi-Priya | Cloud-OS-AI-DB")

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
