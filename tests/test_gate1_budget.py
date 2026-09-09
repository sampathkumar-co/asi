import unittest

from seed.core.budget import Budget, BudgetExceeded
from seed.providers.base import Message
from seed.providers.budgeted import BudgetedProvider
from seed.providers.scripted import ScriptedProvider


class Gate1BudgetTests(unittest.TestCase):
    def test_hard_model_call_limit(self):
        b = Budget(max_model_calls=1, max_tokens=100, max_cost_usd=1)
        p = BudgetedProvider(ScriptedProvider(["a", "b"]), b, provider_id="same-model")
        p.complete([Message("user", "x")], purpose="one")
        with self.assertRaises(BudgetExceeded):
            p.complete([Message("user", "y")], purpose="two")
        self.assertEqual(b.model_calls, 1)

    def test_hard_token_limit(self):
        b = Budget(max_model_calls=2, max_tokens=1, max_cost_usd=1)
        p = BudgetedProvider(ScriptedProvider(["two words"]), b, provider_id="same-model")
        with self.assertRaises(BudgetExceeded):
            p.complete([Message("user", "x")], purpose="one")
        self.assertEqual(b.model_calls, 0)

    def test_transcript_hash_changes_with_calls(self):
        b = Budget(max_model_calls=2, max_tokens=100)
        p = BudgetedProvider(ScriptedProvider(["a"]), b, provider_id="m")
        before = p.transcript_hash
        p.complete([Message("user", "x")], purpose="one")
        self.assertNotEqual(before, p.transcript_hash)

    def test_negative_limits_rejected(self):
        with self.assertRaises(ValueError):
            Budget(max_steps=-1)


if __name__ == "__main__":
    unittest.main()
