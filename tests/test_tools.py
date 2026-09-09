import unittest
from seed.tools.builtin import calculator, default_registry

class ToolTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculator({"expression": "2 + 3*4"}).output, 14)

    def test_calculator_rejects_code(self):
        result = calculator({"expression": "__import__('os').system('echo bad')"})
        self.assertFalse(result.ok)

    def test_unknown_tool_denied(self):
        result = default_registry().call("shell", {"command": "whoami"})
        self.assertFalse(result.ok)
        self.assertIn("not allowed", result.error)

if __name__ == "__main__": unittest.main()
