import unittest

from seed.eval.cases import EvalCase, exact_match
from seed.eval.resources import MeasuredOutput, ResourceUsage
from seed.eval.suite import EvalSuite


class MeasuredEvalTests(unittest.TestCase):
    def test_usage_flows_into_metrics_and_receipt(self):
        suite = EvalSuite("measured", [EvalCase("1", "x", exact_match("x"))])

        def candidate(prompt):
            return MeasuredOutput(
                prompt,
                ResourceUsage(
                    model_calls=1,
                    tool_calls=2,
                    input_tokens=10,
                    output_tokens=5,
                    cost_usd=0.01,
                    compute_seconds=0.25,
                ),
            )

        out = suite.run("candidate", candidate)
        self.assertEqual(out.score, 1.0)
        self.assertEqual(out.metrics.model_calls, 1)
        self.assertEqual(out.metrics.tool_calls, 2)
        self.assertEqual(out.metrics.tokens, 15)
        self.assertEqual(out.metrics.cost_usd, 0.01)
        self.assertEqual(out.receipt.metrics["tokens"], 15)
        self.assertEqual(out.receipt.metrics["compute_seconds"], 0.25)


if __name__ == "__main__":
    unittest.main()
