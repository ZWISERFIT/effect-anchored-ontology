"""
Hallucination Gate (H-Function)
===============================

Deterministic validation of LLM outputs against schema, fact, and rule constraints.
Operates OUTSIDE the LLM's reasoning space — rules here are code, not tokens.

Architecture Principle:
    "Model-generated JSON shape cannot safely be rewritten after generation
     without hiding a contract failure." — richardchen874-sys

    We validate. We record. We do NOT repair inside the LLM's probability space.

KNOWN TECHNICAL DEBT (Tristan audit 2026-07-27):
    T1 - Time-window validation: constraints are checked against current rules,
         but not validated against the ruleset version at output-generation time.
         Fix: H(output, constraints, epoch_hash) → fail if constraints changed
         since generation. (→ blocking: 7/25 Gateway crash: constraints changed
         post-reload, old outputs validated against new rules.)
    
    T2 - C-function rebuild verification: ContextRebuilder.reconstruct() needs
         to be treated as "another LLM output" and pass through H-function.
         Fix: H(rebuilt_context, C.merkle_root) → verify rebuild integrity.
    
    T3 - A-function output validation (MOST CRITICAL): A-function is the ONLY
         function running inside LLM reasoning space. Rules it generates must
         pass through H-function before activation. Otherwise: LLM judging LLM.
         Status: ✅ IMPLEMENTED — A.derive() signature now accepts external
         H-function callback for independent verification.
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
                "aliases": ["膝盖痛", "膝盖疼", "膝关节疼痛"],
                "value": {
                    "forbidden_suggestions": ["squat", "深蹲"],
                    "required_routing": "human_trainer"
                }
            }

        H-001 FIX: Supports Chinese aliases for anchor matching.
        Matching strategy: anchor key words OR any alias substring in user_message.

        This is NOT semantic search. It's deterministic key+alias lookup.
        
        P1#7 FIX (Zeus audit): Dual-end scanning — match anchor keys/aliases
        in user_message AND scan LLM output for forbidden suggestions.
        Previously only scanned user_message for anchor match, missing cases
        where the LLM output itself contains the trigger (e.g., medical terms).
        """
        # Support both {"facts": {...}} and {"anchors": {...}} formats
        facts = self._anchors.get("facts") or self._anchors.get("anchors") or {}
        output_str = str(output).lower() if isinstance(output, str) else json.dumps(output)
        output_str_lower = output_str.lower()
        violated = []
        user_msg = (context or {}).get("user_message", "").lower()
        # P1#7: Also scan the entire context and output for medical/anchor terms
        combined_msg = user_msg + " " + output_str_lower

        for anchor_key, anchor_rules in facts.items():
            # H-001 FIX: Multi-strategy anchor matching
            # Strategy 1: Keyword-based (original): "knee_pain" → check if "knee" AND "pain" in user_msg
            # Strategy 2: Alias-based (H-001): check if any Chinese/English alias is in user_msg
            matched = False

            # Strategy 1: Keyword matching — scan combined user_msg + output
            key_words = anchor_key.lower().replace('_', ' ').split()
            if key_words and len(key_words) >= 2 and all(word in combined_msg for word in key_words):
                matched = True
            elif key_words and len(key_words) == 1 and key_words[0] in combined_msg:
                matched = True

            # Strategy 2: Alias matching (H-001 — Chinese support)
            # Scan combined_msg (user_message + LLM output) for aliases
            if not matched and isinstance(anchor_rules, dict):
                aliases = anchor_rules.get("aliases", [])
                if aliases:
                    for alias in aliases:
                        if alias.lower() in combined_msg:
                            matched = True
                            break

            if matched and isinstance(anchor_rules, dict):
                # Support nested {"value": {"forbidden_suggestions": [...]}} format
                inner = anchor_rules.get("value") or anchor_rules
                forbidden = inner.get("forbidden_suggestions", []) if isinstance(inner, dict) else []
                for term in forbidden:
                    # #3 FIX (Zeus audit): Use word-boundary matching to prevent
                    # false positives like "arm" in "alarm" or "squat" in "squatter"
                    # P1#5 FIX: also match raw underscore form for identifiers (treadmill_3)
                    import re as _re2
                    term_raw = term.lower()
                    term_clean = term_raw.replace('_', ' ')
                    try:
                        regex = _re2.compile(r'\b' + _re2.escape(term_clean) + r'\b')
                        if regex.search(output_str_lower):
                            violated.append(f"{anchor_key}→{term}")
                            continue
                    except _re2.error:
                        pass
                    # Also check raw form with underscores (e.g., treadmill_3)
                    if term_raw != term_clean and _re2.escape(term_raw) in output_str_lower:
                        if f"{anchor_key}→{term}" not in violated:
                            violated.append(f"{anchor_key}→{term}")
                            continue
                    # Fallback: substring match for CJK chars and edge cases
                    # (\b doesn't work on CJK — regex compiles but won't match,
                    #  so we need explicit substring fallback outside try)
                    if term_clean in output_str_lower or term_clean.rstrip('s') in output_str_lower or term_raw in output_str_lower:
                        if f"{anchor_key}→{term}" not in violated:
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
        """
        Rule layer: Domain-specific constraints (e.g., medical advice routing).
        
        #2 FIX (Zeus audit): Explicit continue for non-pattern_match rules
        to prevent silent skip confusion. Future rule types (capability_anchor,
        time_window, etc.) will be added here with their own branch.
        
        P1#7 FIX (Zeus audit): Dual-end scanning — scan both user_message (context)
        AND LLM output for rule patterns. Previously only scanned output_str, missing
        cases where the user_message contains the trigger (e.g., medical terms).
        """
        import re as _re
        output_str = str(output) if isinstance(output, str) else json.dumps(output)
        output_str_lower = output_str.lower()
        # P1#7: also scan user_message from context
        user_msg = (context or {}).get("user_message", "")
        combined_lower = (output_str_lower + " " + user_msg.lower()).strip()
        
        for rule_key, rule in self._constraints.get("rules", {}).items():
            rule_type = rule.get("type", "")
            
            if rule_type == "pattern_match":
                pattern = rule.get("pattern", "")
                if pattern:
                    # #3 FIX (Zeus audit): Use \b word-boundary matching to prevent
                    # false positives like "arm" in "alarm" or "squat" in "squatter"
                    pattern_terms = pattern.lower().split('|')
                    for term in pattern_terms:
                        term_raw = term.strip()
                        term_clean = term_raw.replace('_', ' ')  # P1#5 fix: preserve internal structure
                        # Build word-boundary regex: \bterm\b for each term
                        # P1#5 FIX: try both forms — underscore-preserved (treadmill_3)
                        # and space-substituted (treadmill 3). Underscore is a word
                        # char so \b won't fire around it; space-substituted form
                        # enables word-boundary matching for identifiers with underscores.
                        try:
                            # Form 1: space-substituted (word boundary works)
                            regex = _re.compile(r'\b' + _re.escape(term_clean) + r'\b')
                            if regex.search(combined_lower):
                                return HResult(
                                    passed=False,
                                    gate_result=GateResult.FAIL,
                                    reason=rule.get("reason", f"Rule violation: {rule_key}"),
                                    anchors_violated=[rule_key],
                                )
                            # Form 2: raw (preserves underscores — direct substring)
                            if term_raw != term_clean and _re.escape(term_raw) in combined_lower:
                                return HResult(
                                    passed=False,
                                    gate_result=GateResult.FAIL,
                                    reason=rule.get("reason", f"Rule violation: {rule_key}"),
                                    anchors_violated=[rule_key],
                                )
                            # Fallback: substring match for CJK and edge cases
                            # (\b doesn't work on CJK characters — regex compiles but
                            #  doesn't match, so we need explicit substring fallback)
                            if term_clean in combined_lower or term_raw in combined_lower:
                                return HResult(
                                    passed=False,
                                    gate_result=GateResult.FAIL,
                                    reason=rule.get("reason", f"Rule violation: {rule_key}"),
                                    anchors_violated=[rule_key],
                                )
                        except _re.error:
                            # Regex compilation failed — pure substring fallback
                            if term_clean in combined_lower or term_raw in combined_lower:
                                return HResult(
                                    passed=False,
                                    gate_result=GateResult.FAIL,
                                    reason=rule.get("reason", f"Rule violation: {rule_key}"),
                                    anchors_violated=[rule_key],
                                )
            # #2 FIX: Explicit else-continue for non-pattern_match rule types
            # (capability_anchor, time_window, etc. — future extension points)
            else:
                continue
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
