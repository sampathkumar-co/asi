import unittest
from seed.core.memory import MemoryStore


class MemoryTests(unittest.TestCase):
    def test_append_and_recent(self):
        with MemoryStore(":memory:") as m:
            m.append("r", "hypothesis", "first", tags=("a",))
            m.append("r", "result", "second")
            rows = m.recent("r", limit=10)
            self.assertEqual([x.content for x in rows], ["first", "second"])
            self.assertEqual(m.recent("r", kind="result")[0].content, "second")


if __name__ == "__main__":
    unittest.main()
