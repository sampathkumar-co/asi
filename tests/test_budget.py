import unittest

from seed.core.budget import Budget, BudgetExceeded


class BudgetTests(unittest.TestCase):
    def test_step_limit(self):
        b = Budget(max_steps=1)
        self.assertTrue(b.can_step())
        b.charge_step()
        self.assertFalse(b.can_step())
        with self.assertRaises(BudgetExceeded):
            b.charge_step()

    def test_cost_limit_is_hard(self):
        b = Budget(max_cost_usd=1.0)
        with self.assertRaises(BudgetExceeded):
            b.charge_model(cost_usd=1.1)
        self.assertEqual(b.model_calls, 0)
        self.assertEqual(b.cost_usd, 0.0)

    def test_tool_limit_is_hard(self):
        b = Budget(max_tool_calls=0)
        with self.assertRaises(BudgetExceeded):
            b.charge_tool()


if __name__ == "__main__":
    unittest.main()
