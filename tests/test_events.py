import os
import tempfile
import unittest

from seed.core.events import EventStore


class EventStoreTests(unittest.TestCase):
    def test_hash_chain_verifies(self):
        with tempfile.TemporaryDirectory() as d:
            with EventStore(os.path.join(d, "events.db")) as store:
                store.append("r1", "a", {"x": 1})
                store.append("r1", "b", {"x": 2})
                self.assertTrue(store.verify_chain("r1"))
                self.assertEqual(len(store.list("r1")), 2)

    def test_runs_have_separate_genesis(self):
        with EventStore(":memory:") as store:
            a = store.append("a", "x", {})
            b = store.append("b", "x", {})
            self.assertEqual(a.prev_hash, "GENESIS")
            self.assertEqual(b.prev_hash, "GENESIS")

    def test_closed_store_fails_cleanly(self):
        store = EventStore(":memory:")
        store.close()
        with self.assertRaises(RuntimeError):
            store.list("r1")


if __name__ == "__main__":
    unittest.main()
