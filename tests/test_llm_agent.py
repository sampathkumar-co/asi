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
        with self.assertRaises(PermissionError):
            JSONPlanner(p, ("calculator",)).next_task(AgentState(Goal("g")))

    def test_planner_rejects_missing_required_tool_input(self):
        p = ScriptedProvider(['{"description":"note","tool_name":"echo","tool_input":{"other":"wrong"}}'])
        with self.assertRaises(ValueError):
            JSONPlanner(p, ("echo",)).next_task(AgentState(Goal("g")))

    def test_planner_normalizes_message_alias(self):
        p = ScriptedProvider(['{"description":"note","tool_name":"echo","tool_input":{"message":"evidence"}}'])
        task = JSONPlanner(p, ("echo",)).next_task(AgentState(Goal("g")))
        self.assertEqual(task.tool_input, {"text": "evidence"})

    def test_planner_normalizes_nested_call(self):
        p = ScriptedProvider(['{"description":"note","tool_name":"echo","tool_input":{"tool_name":"echo","tool_input":{"text":"evidence"}}}'])
        task = JSONPlanner(p, ("echo",)).next_task(AgentState(Goal("g")))
        self.assertEqual(task.tool_input, {"text": "evidence"})

    def test_planner_accepts_exact_echo_schema(self):
        p = ScriptedProvider(['{"description":"note","tool_name":"echo","tool_input":{"text":"evidence"}}'])
        task = JSONPlanner(p, ("echo",)).next_task(AgentState(Goal("g")))
        self.assertEqual(task.tool_input, {"text": "evidence"})

    def test_critic_threshold_blocks_weak_done(self):
        p = ScriptedProvider(['{"done":true,"confidence":0.6,"reason":"weak","final_answer":"x"}'])
        c = JSONCritic(p, finish_threshold=0.85).review(AgentState(Goal("g")))
        self.assertFalse(c.done)
        self.assertIsNone(c.final_answer)

if __name__ == "__main__": unittest.main()
