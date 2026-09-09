import unittest
from seed.agent.baseline import BaselineAgent
from seed.agent.components import CompletionCritic, QueuePlanner, RegistryExecutor
from seed.core.budget import Budget
from seed.core.models import Goal, RunStatus, Task
from seed.tools.builtin import default_registry

class AgentTests(unittest.TestCase):
    def test_baseline_completes(self):
        tasks = [Task("math", "calculator", {"expression": "6*7"})]
        state = BaselineAgent(QueuePlanner(tasks), RegistryExecutor(default_registry()), CompletionCritic(1)).run(Goal("answer"))
        self.assertEqual(state.status, RunStatus.SUCCEEDED)
        self.assertEqual(state.final_answer, "42")

    def test_budget_stops_agent(self):
        tasks = [Task("bad", "missing", {}) for _ in range(5)]
        state = BaselineAgent(QueuePlanner(tasks), RegistryExecutor(default_registry()), CompletionCritic(1), budget=Budget(max_steps=2)).run(Goal("bounded"))
        self.assertEqual(state.status, RunStatus.BUDGET_EXHAUSTED)
        self.assertEqual(state.step, 2)

if __name__ == "__main__": unittest.main()
