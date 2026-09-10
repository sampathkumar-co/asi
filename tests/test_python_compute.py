import unittest

from seed.tools.builtin import default_registry
from seed.tools.python_compute import python_compute


class PythonComputeTests(unittest.TestCase):
    def test_computation_returns_json_value(self):
        result = python_compute({"code": "xs=[i*i for i in range(6)]\nresult=sum(xs)"})
        self.assertTrue(result.ok)
        self.assertEqual(result.output, 55)

    def test_combinatorics_helpers_are_available(self):
        result = python_compute({"code": "vals=[p for p in permutations([1,2,3]) if p[0]==2]\nresult=len(vals)"})
        self.assertTrue(result.ok)
        self.assertEqual(result.output, 2)

    def test_safe_imports_are_canonicalized(self):
        code = "from collections import defaultdict\nd=defaultdict(list)\nd['x'].append(4)\nresult=d.get('x')"
        result = python_compute({"code": code})
        self.assertTrue(result.ok)
        self.assertEqual(result.output, [4])

    def test_safe_string_join_is_available(self):
        result = python_compute({"code": "parts=['A','B','C']\nresult='-'.join(parts)"})
        self.assertTrue(result.ok)
        self.assertEqual(result.output, "A-B-C")

    def test_duplicate_line_continuation_is_canonicalized(self):
        code = "x=True and " + ("\\" * 2) + "\n True\nresult=x"
        result = python_compute({"code": code})
        self.assertTrue(result.ok)
        self.assertIs(result.output, True)

    def test_import_and_attribute_access_are_blocked(self):
        self.assertFalse(python_compute({"code": "import os\nresult=1"}).ok)
        self.assertFalse(python_compute({"code": "result=(1).__class__"}).ok)
        self.assertFalse(python_compute({"code": "result='x'.encode()"}).ok)

    def test_result_is_required(self):
        result = python_compute({"code": "x=2+2"})
        self.assertFalse(result.ok)

    def test_default_registry_exposes_python_compute(self):
        result = default_registry().call("python_compute", {"code": "result=6*7"})
        self.assertTrue(result.ok)
        self.assertEqual(result.output, 42)


if __name__ == "__main__":
    unittest.main()
