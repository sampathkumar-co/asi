import unittest
from seed.selfmod.lineage import LineageStore

class LineageTests(unittest.TestCase):
    def test_lineage_and_ancestors(self):
        s = LineageStore(":memory:")
        s.add_candidate("a", None, "p0", "h0")
        s.add_candidate("b", "a", "p1", "h1")
        s.add_candidate("c", "b", "p2", "h2")
        self.assertEqual([n.candidate_id for n in s.ancestors("c")], ["c", "b", "a"])
        s.record("c", "eval", {"score": 0.9})

    def test_missing_parent_rejected(self):
        s = LineageStore(":memory:")
        with self.assertRaises(ValueError): s.add_candidate("b", "missing", "p", "h")

if __name__ == "__main__": unittest.main()
