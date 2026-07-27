"""
Hallucination Gate (H-Function)
===============================

Deterministic validation of LLM outputs against schema, fact, and rule constraints.
Operates OUTSIDE the LLM's reasoning space — rules here are code, not tokens.

Architecture Principle:
    "Model-generated JSON shape cannot safely be rewritten after generation
     without hiding a contract failure." — richardchen874-sys

    We validate. We record. We do NOT repair inside the LLM's probability space.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class GateResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    REPAIR = "repair"  # external deterministic fix applied (not LLM-space repair)


@dataclass
class HResult:
    """Result of a hallucination gate check."""
    passed: bool
    gate_result: GateResult
    reason: Optional[str] = None
    anchors_violated: List[str] = field(default_factory=list)
    repair_applied: Optional[str] = None  # description of external fix
    evidence: Optional[Dict[str, Any]] = None  # for RetroOnto decision tracing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "gate_result": self.gate_result.value,
            "reason": self.reason,
            "anchors_violated": self.anchors_violated,
            "repair_applied": self.repair_applied,
            "evidence": self.evidence,
        }


class HallucinationGate:
    """
    H-Function: External hallucination suppressor.

    Architecture:
        LLM output → HallucinationGate.check() → PASS/FAIL/REPAIR
        ↑                               ↑
        LLM reasoning space             Deterministic space (this library)

    Three validation layers (checked sequentially, short-circuit on FAIL):
        1. Schema validation: Does the output match the expected JSON schema?
        2. Fact validation: Does the output contradict known hard-coded facts?
        3. Rule validation: Does the output violate domain-specific rules?

    Key invariant:
        This function NEVER modifies the LLM output inside the LLM's probability
        space. REPAIR operations are external, deterministic, and traceable.
    """

    def __init__(
        self,
        constraints_path: Optional[str] = None,
        anchors_path: Optional[str] = None,
    ):
        """
        Args:
            constraints_path: Path to JSON file with schema/rules/domain constraints.
            anchors_path: Path to JSON file with hard-coded fact anchors.
        """
        self._constraints = self._load_json(constraints_path) if constraints_path else {}
        self._anchors = self._load_json(anchors_path) if anchors_path else {}
        self._violation_log: List[Dict[str, Any]] = []

    def check(
        self,
        llm_output: Any,
        context: Optional[Dict[str, Any]] = None,
        expected_schema: Optional[Dict[str, Any]] = None,
    ) -> HResult:
        """
        Validate an LLM output against all constraint layers.

        Args:
            llm_output: The raw output from the LLM (string, dict, or parsed JSON).
            context: Optional context about the interaction (user query, intent, etc.).
            expected_schema: Optional JSON schema to validate against.

        Returns:
            HResult with pass/fail/repair status and violation details.

        Side effects:
            - FAIL results are logged to violation_log for A-function processing.
            - All results are structured for RetroOnto decision tracing.
        """
        # Layer 1: Schema validation
        if expected_schema:
            schema_result = self._validate_schema(llm_output, expected_schema)
            if not schema_result.passed:
                self._log_violation("schema", schema_result)
                return schema_result

        # Layer 2: Fact validation
        fact_result = self._validate_facts(llm_output, context)
        if not fact_result.passed:
            self._log_violation("fact", fact_result)
            return fact_result

        # Layer 3: Rule validation
        rule_result = self._validate_rules(llm_output, context)
        if not rule_result.passed:
            self._log_violation("rule", rule_result)
            return rule_result

        return HResult(passed=True, gate_result=GateResult.PASS)

    def _validate_schema(self, output: Any, schema: Dict) -> HResult:
        """Schema layer: structural validation. Deterministic, no LLM involved."""
        # In MVP: jsonschema.validate() or equivalent
        # For now: interface definition
        try:
            if isinstance(output, str):
                output = json.loads(output)
            # jsonschema.validate(output, schema)  # MVP implementation
            return HResult(passed=True, gate_result=GateResult.PASS)
        except Exception as e:
            return HResult(
                passed=False,
                gate_result=GateResult.FAIL,
                reason=f"Schema validation failed: {str(e)}",
                evidence={"output_preview": str(output)[:200]},
            )

    def _validate_facts(
        self, output: Any, context: Optional[Dict] = None
    ) -> HResult:
        """
        Fact layer: Check against hard-coded anchors.

        Example anchor:
            "knee_pain": {
                "forbidden_suggestions": ["squat", "leg_press", "lunge"],
                "required_routing": "human_trainer"
            }

        This is NOT semantic search. It's deterministic key lookup.
        """
        output_str = str(output).lower() if isinstance(output, str) else json.dumps(output)
        violated = []
        for anchor_key, anchor_rules in self._anchors.get("facts", {}).items():
            if anchor_key.lower() in (context or {}).get("user_message", "").lower():
                if isinstance(anchor_rules, dict):
                    forbidden = anchor_rules.get("forbidden_suggestions", [])
                    for term in forbidden:
                        if term.lower() in output_str:
                            violated.append(f"{anchor_key}→{term}")

        if violated:
            return HResult(
                passed=False,
                gate_result=GateResult.FAIL,
                reason="Fact anchors violated",
                anchors_violated=violated,
                evidence={"matched_anchors": violated},
            )
        return HResult(passed=True, gate_result=GateResult.PASS)

    def _validate_rules(
        self, output: Any, context: Optional[Dict] = None
    ) -> HResult:
        """Rule layer: Domain-specific constraints (e.g., medical advice routing)."""
        for rule_key, rule in self._constraints.get("rules", {}).items():
            if rule.get("type") == "pattern_match":
                pattern = rule.get("pattern", "")
                output_str = str(output) if isinstance(output, str) else json.dumps(output)
                if pattern and pattern.lower() in output_str.lower():
                    return HResult(
                        passed=False,
                        gate_result=GateResult.FAIL,
                        reason=rule.get("reason", f"Rule violation: {rule_key}"),
                        anchors_violated=[rule_key],
                    )
        return HResult(passed=True, gate_result=GateResult.PASS)

    def _log_violation(self, layer: str, result: HResult) -> None:
        """Log violation for A-function processing and RetroOnto tracing."""
        self._violation_log.append({
            "layer": layer,
            "result": result.to_dict(),
            "timestamp": None,  # inject timestamp at call site
        })

    @staticmethod
    def _load_json(path: str) -> Dict:
        """Load JSON constraint/anchor file. Deterministic file I/O."""
        with open(path, "r") as f:
            return json.load(f)
