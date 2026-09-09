import unittest
from seed.providers.base import Message
from seed.providers.scripted import ScriptedProvider

class ProviderTests(unittest.TestCase):
    def test_scripted_provider(self):
        p = ScriptedProvider(["ok"]); r = p.complete([Message("user", "hello")], purpose="test")
        self.assertEqual(r.text, "ok"); self.assertGreater(r.total_tokens, 0)

    def test_scripted_exhaustion(self):
        with self.assertRaises(RuntimeError): ScriptedProvider([]).complete([], purpose="x")

if __name__ == "__main__": unittest.main()
