import os, tempfile, unittest
from seed.core.events import EventStore

class EventStoreTests(unittest.TestCase):
    def test_hash_chain_verifies(self):
        with tempfile.TemporaryDirectory() as d:
            store = EventStore(os.path.join(d, "events.db"))
            store.append("r1", "a", {"x": 1})
            store.append("r1", "b", {"x": 2})
            self.assertTrue(store.verify_chain("r1"))
            self.assertEqual(len(store.list("r1")), 2)

    def test_runs_have_separate_genesis(self):
        store = EventStore(":memory:")
        a = store.append("a", "x", {})
        b = store.append("b", "x", {})
        self.assertEqual(a.prev_hash, "GENESIS")
        self.assertEqual(b.prev_hash, "GENESIS")

if __name__ == "__main__": unittest.main()
