import unittest

from seed.agent.llm import _verified_answers
from seed.agent.tool_routing import select_tools
from seed.core.models import AgentState, Goal, Observation
from seed.tools.assignment import assignment_csp_tool
from seed.tools.python_trace import python_trace
from seed.tools.subset_optimize import subset_optimize
from seed.tools.transactions import transaction_ledger

class ExactToolsV2Tests(unittest.TestCase):
    def test_transaction_ledger_uses_semantic_sale_math(self):
        result=transaction_ledger({
            'records':[
                {'group':'A','status':'POSTED','kind':'sale','quantity':3,'unit_price':40,'discount_percent':10},
                {'group':'A','status':'POSTED','kind':'refund','amount':25},
                {'group':'B','status':'POSTED','kind':'credit','amount':11.5}],
            'include_statuses':['POSTED'],'answer_template':'FINAL: A={A},B={B},TOTAL={TOTAL}'})
        self.assertTrue(result.ok)
        self.assertEqual(result.output['answer'],'FINAL: A=83.00,B=11.50,TOTAL=94.50')

    def test_transaction_ledger_parses_verbatim_record_text(self):
        text='Only CLEARED records count. P sale 3*42 with 10% discount CLEARED; Q sale 2*65 CLEARED; P refund 18.50 CLEARED; R sale 4*31.25 CLEARED; Q fee 7.25 CLEARED; R refund 12 CLEARED; Q sale 3*40 with 5% discount CLEARED. Return exactly: FINAL: ...'
        result=transaction_ledger({'records_text':text,'include_statuses':['CLEARED'],'answer_template':'FINAL: P={P},Q={Q},R={R},TOTAL={TOTAL}'})
        self.assertTrue(result.ok)
        self.assertEqual(result.output['answer'],'FINAL: P=94.90,Q=236.75,R=113.00,TOTAL=444.65')

    def test_transaction_ledger_normalizes_safe_field_aliases(self):
        result=transaction_ledger({'records':[{'group':'A','status':'X','kind':'sale','qty':2,'unit,':4}], 'include_statuses':['X'],'answer_template':'FINAL: A={A},TOTAL={TOTAL}'})
        self.assertTrue(result.ok)
        self.assertEqual(result.output['answer'],'FINAL: A=8.00,TOTAL=8.00')

    def test_transaction_ledger_rejects_ambiguous_sale(self):
        result=transaction_ledger({'records':[{'group':'A','status':'X','kind':'sale','amount':3,'quantity':2,'unit_price':4}], 'include_statuses':['X'],'answer_template':'FINAL: {TOTAL}'})
        self.assertFalse(result.ok)

    def test_python_trace_executes_exact_source_and_captures_print(self):
        code='a=[2,3,4]\nb=a\nr=[]\nfor i,x in enumerate(a):\n    if x%2==0: a[i]=x+i\n    else: r.append(x*i)\nb[0]+=1\nprint(a,r,sum(b))'
        result=python_trace({'code':code,'print_index':3})
        self.assertTrue(result.ok)
        self.assertEqual(result.output['answer'],'FINAL: [3, 3, 6] | [3] | 12')

    def test_python_trace_blocks_imports(self):
        self.assertFalse(python_trace({'code':'import os\nprint(1)'}).ok)

    def test_subset_optimizer_distinguishes_implies_and_exclusive(self):
        result=subset_optimize({'items':[
            {'name':'A','weight':3,'value':7},{'name':'B','weight':4,'value':10},
            {'name':'C','weight':5,'value':13},{'name':'D','weight':2,'value':6}],
            'capacity':9,'constraints':{'implies':[['C','D']], 'exclusive':[['A','B']]},
            'answer_template':'FINAL: {value} | {items}'})
        self.assertTrue(result.ok)
        self.assertEqual(result.output['answer'],'FINAL: 19 | CD')

    def test_assignment_single_character_labels_default_to_no_separator(self):
        result=assignment_csp_tool({'groups':{'jobs':['A','B','C']},'positions':[1,2,3],
            'constraints':['before(B,A)','before(A,C)'],'labels':{},
            'render_groups':[{'name':'jobs','group':'jobs'}],'answer_template':'FINAL: {jobs}'})
        self.assertTrue(result.ok)
        self.assertEqual(result.output['answer'],'FINAL: BAC')

    def test_routing_selects_new_exact_tools(self):
        available=('transaction_ledger','python_trace','subset_optimize','python_compute','calculator')
        self.assertIn('transaction_ledger',select_tools('Reconcile APPROVED credits and debits by account.',available))
        self.assertIn('python_trace',select_tools('Trace this Python code and report print(a): for i in range(3): pass',available))
        self.assertIn('subset_optimize',select_tools('Items have weight and value. Capacity 15. Find maximum total value subset.',available))

    def test_verified_evidence_normalizes_missing_final_prefix(self):
        state=AgentState(Goal('x'))
        state.observations.append(Observation('t',True,{'answer':'20 | A-C-E-G-I','checks':{'ok':True}}))
        self.assertEqual(_verified_answers(state),('FINAL: 20 | A-C-E-G-I',))

if __name__ == '__main__':
    unittest.main()

