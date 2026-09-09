import unittest
from seed.core.budget import Budget

class BudgetTests(unittest.TestCase):
    def test_step_limit(self):
        b = Budget(max_steps=1)
        self.assertTrue(b.can_step()); b.charge_step(); self.assertFalse(b.can_step())

    def test_cost_limit(self):
        b = Budget(max_cost_usd=1.0); b.charge_model(cost_usd=1.1); self.assertFalse(b.can_step())

if __name__ == "__main__": unittest.main()
