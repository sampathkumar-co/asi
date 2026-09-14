import json
import unittest
from pathlib import Path

from seed.gate2.local_campaign import (
    ModelProtocolError,
    _SCHEMA_REPAIR_CALL_LIMIT_PER_ARM,
    _SchemaRepairState,
    _budget,
    _run_arm,
    _validate_with_schema_repairs,
    _validated_attribution,
)
from seed.gate2.schema import load_research_tasks
from seed.providers.budgeted import BudgetedProvider
from seed.providers.scripted import ScriptedProvider


class Gate2BoundedRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        _, tasks = load_research_tasks(root / "configs/gate2_public_calibration_v1.json")
        cls.task = tasks[0]

    def meter(self, responses: list[str]):
        budget = _budget()
        provider = BudgetedProvider(
            ScriptedProvider(responses), budget, provider_id="ollama:qwen3:8b"
        )
        return provider, budget
    def structurally_valid_attribution(self) -> dict:
        hid = self.task.hypotheses[0].id
        return {
            "outcome_support": {
                experiment.id: {
                    outcome.id: [hid]
                    for outcome in experiment.possible_outcomes
                }
                for experiment in self.task.experiments
            }
        }

    def validate(self, provider, budget, initial, state, events, stage="attribution"):
        return _validate_with_schema_repairs(
            provider, budget, self.task, arm="seed", stage=stage,
            data=initial, validator=lambda value: _validated_attribution(self.task, value),
            history=[], revisions=[], repair_state=state, repair_events=events,
        )

    def test_second_schema_repair_can_recover(self):
        malformed = {"outcome_support": {}}
        still_malformed = {"outcome_support": {self.task.experiments[0].id: {}}}
        valid = self.structurally_valid_attribution()
        provider, budget = self.meter([json.dumps(still_malformed), json.dumps(valid)])
        state = _SchemaRepairState()
        events: list[dict[str, str]] = []

        result = self.validate(provider, budget, malformed, state, events)

        self.assertEqual(len(result), sum(len(e.possible_outcomes) for e in self.task.experiments))
        self.assertEqual(state.used, 2)
        self.assertEqual([event["attempt"] for event in events], ["1", "2"])
        self.assertEqual([record.purpose for record in provider.records], ["gate2_repair", "gate2_repair"])
    def test_third_schema_repair_is_never_attempted(self):
        malformed = {"outcome_support": {}}
        provider, budget = self.meter([
            json.dumps(malformed), json.dumps(malformed), json.dumps(self.structurally_valid_attribution())
        ])
        state = _SchemaRepairState()
        events: list[dict[str, str]] = []

        with self.assertRaises(ModelProtocolError):
            self.validate(provider, budget, malformed, state, events)

        self.assertEqual(_SCHEMA_REPAIR_CALL_LIMIT_PER_ARM, 2)
        self.assertEqual(state.used, 2)
        self.assertEqual(len(events), 2)
        self.assertEqual(len(provider.records), 2)
        self.assertEqual(budget.model_calls, 2)

    def test_repair_budget_is_shared_across_stages(self):
        malformed = {"outcome_support": {}}
        valid = self.structurally_valid_attribution()
        provider, budget = self.meter([json.dumps(valid), json.dumps(valid)])
        state = _SchemaRepairState()
        events: list[dict[str, str]] = []

        self.validate(provider, budget, malformed, state, events, stage="first")
        self.validate(provider, budget, malformed, state, events, stage="second")
        with self.assertRaises(ModelProtocolError):
            self.validate(provider, budget, malformed, state, events, stage="third")

        self.assertEqual(state.used, 2)
        self.assertEqual([event["stage"] for event in events], ["first", "second"])
        self.assertEqual(len(provider.records), 2)


    def test_seed_arm_recovers_when_second_attribution_repair_is_valid(self):
        hypotheses = [h.id for h in self.task.hypotheses]
        malformed = {"outcome_support": {}}
        still_malformed = {"outcome_support": {self.task.experiments[0].id: {}}}
        valid = {
            "outcome_support": {
                experiment.id: {
                    outcome.id: list(hypotheses)
                    for outcome in experiment.possible_outcomes
                }
                for experiment in self.task.experiments
            }
        }
        design = {"control_ids": [], "risk_ids": [], "reason": "bounded public-development design"}
        final = {
            "final_hypothesis_id": hypotheses[0], "rejected_hypothesis_ids": [],
            "risk_ids": [], "confidence": 0.5, "reason": "runner conclusion explanation",
        }
        verifier = {
            "supported_hypothesis_ids": list(hypotheses), "has_direct_evidence_defect": False,
            "defect_summary": "none", "confidence": 0.9, "risk_ids": [],
            "reason": "structurally complete public-development verifier",
        }
        responses = [
            json.dumps(malformed), json.dumps(still_malformed), json.dumps(valid),
            json.dumps(design), json.dumps(design), json.dumps(final),
            json.dumps(verifier), json.dumps(verifier),
        ]
        provider, budget = self.meter(responses)

        arm = _run_arm(self.task, provider, budget, "seed")

        self.assertEqual(arm.status, "succeeded")
        self.assertEqual(arm.failure_kind, None)
        self.assertEqual(len(arm.repair_events), 2)
        self.assertEqual([event["stage"] for event in arm.repair_events], ["attribution", "attribution"])
        self.assertEqual([event["repair_index"] for event in arm.repair_events], ["1", "2"])
        self.assertEqual(arm.call_purposes[:3],
                         ("gate2_seed_attribute_outcomes", "gate2_repair", "gate2_repair"))
        self.assertEqual(arm.usage["model_calls"], 8)

    def test_verifier_repairs_use_shared_budget_and_are_recorded(self):
        hypotheses = [h.id for h in self.task.hypotheses]
        attribution = {
            "outcome_support": {
                experiment.id: {outcome.id: list(hypotheses) for outcome in experiment.possible_outcomes}
                for experiment in self.task.experiments
            }
        }
        design = {"control_ids": [], "risk_ids": [], "reason": "bounded design"}
        final = {
            "final_hypothesis_id": hypotheses[0], "rejected_hypothesis_ids": [],
            "risk_ids": [], "confidence": 0.5, "reason": "runner will preserve its conclusion",
        }
        bad_verifier = {
            "supported_hypothesis_ids": [], "has_direct_evidence_defect": False,
            "defect_summary": "none", "confidence": 0.9, "risk_ids": [], "reason": "incomplete support set",
        }
        good_verifier = {
            "supported_hypothesis_ids": list(hypotheses), "has_direct_evidence_defect": False,
            "defect_summary": "none", "confidence": 0.9, "risk_ids": [], "reason": "all tied hypotheses included",
        }
        responses = [
            json.dumps(attribution), json.dumps(design), json.dumps(design), json.dumps(final),
            json.dumps(bad_verifier), json.dumps(bad_verifier), json.dumps(good_verifier),
            json.dumps(good_verifier),
        ]
        provider, budget = self.meter(responses)

        arm = _run_arm(self.task, provider, budget, "seed")

        self.assertEqual(arm.status, "succeeded")
        self.assertEqual(arm.failure_kind, None)
        self.assertEqual(len(arm.repair_events), 2)
        self.assertEqual([event["stage"] for event in arm.repair_events],
                         ["independent_verifier", "independent_verifier"])
        self.assertEqual([event["repair_index"] for event in arm.repair_events], ["1", "2"])
        self.assertEqual(arm.call_purposes.count("gate2_repair"), 2)
        self.assertEqual(arm.usage["model_calls"], 8)


if __name__ == "__main__":
    unittest.main()
