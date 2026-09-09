import unittest
from seed.agent.llm import JSONPlanner, JSONCritic
from seed.core.models import AgentState, Goal
from seed.providers.scripted import ScriptedProvider

class LLMAgentTests(unittest.TestCase):
    def test_planner_enforces_tool_allowlist(self):
        p = ScriptedProvider(['{"description":"calc","tool_name":"calculator","tool_input":{"expression":"2+2"}}'])
        task = JSONPlanner(p, ("calculator",)).next_task(AgentState(Goal("g")))
        self.assertEqual(task.tool_name, "calculator")

    def test_planner_rejects_unlisted_tool(self):
        p = ScriptedProvider(['{"description":"shell","tool_name":"shell","tool_input":{}}'])
        with self.assertRaises(PermissionError): JSONPlanner(p, ("calculator",)).next_task(AgentState(Goal("g")))

    def test_critic_threshold_blocks_weak_done(self):
        p = ScriptedProvider(['{"done":true,"confidence":0.6,"reason":"weak","final_answer":"x"}'])
        c = JSONCritic(p, finish_threshold=0.85).review(AgentState(Goal("g")))
        self.assertFalse(c.done)
        self.assertIsNone(c.final_answer)

if __name__ == "__main__": unittest.main()
