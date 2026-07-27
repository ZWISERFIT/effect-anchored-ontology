"""
HallucinationGate (H-function) — External Fact Validation

Validates every factual claim in an agent's output against external
data sources before it reaches the user. Strips unverifiable claims.

Architecture Context:
    H runs as an independent process outside the LLM inference space.
    It intercepts agent output, extracts factual statements via NER,
    cross-references each against registered data sources, and either:
    - ✅ Passes (evidence found, match threshold met)
    - 🔴 Strips the claim (no evidence, or evidence contradicts)

    Not a "guardrail" — a fact verifier. Difference: guardrails detect
    patterns (PII, toxicity). HallucinationGate verifies claims.

Design Principles:
    • Output level, not input level — validates what agent says, not
      what the prompt says
    • Evidence required for every factual claim
    • Honest about what it can't verify — marks as "uncertain"
"""

from typing import Any, Dict, Optional, Tuple


class HallucinationGate:
    """Validates agent factual claims against external constraint sources.

    Parameters
    ----------
    constraints : str
        Path to a JSON or YAML file defining provider rules, registered
        data sources, and validation schemas. Example structure:
        {
            "sources": {
                "store_dashboard": {"type": "api", "url": "...", "api_key_env": "..."},
                "pkb_anchors": {"type": "sqlite", "path": "anchors/facts.db"}
            },
            "validation_rules": {
                "terminated_entity": {"require_source_timestamp": true}
            }
        }
    """

    def __init__(self, constraints: str) -> None:
        self._constraints_path = constraints
        self._sources: Dict[str, Any] = {}

    def validate(
        self,
        output: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate a factual claim in agent output against external sources.

        The validation pipeline:
        1. Extract factual statements from output (NER-based extraction)
        2. Map each statement to a registered data source
        3. Cross-reference statement against source
        4. Return (passed, evidence) or (failed, None with details)

        Parameters
        ----------
        output : str
            The agent's natural language output containing factual claims.
        context : dict, optional
            Optional execution context (e.g., {"source": "store_dashboard",
            "ref": "daily_stats_2026-07-27"}). Helps route to the right source.

        Returns
        -------
        (bool, dict or None)
            - (True, evidence_dict) if claim passes validation
            - (False, detail_dict) if claim fails or cannot be verified
              detail_dict contains reason and uncertainty metadata

        Examples
        --------
        >>> gate = HallucinationGate(constraints="schema/provider_rules.json")
        >>> passed, evidence = gate.validate(
        ...     output="ZWF processes 42 daily visitors on average.",
        ...     context={"source": "store_dashboard"}
        ... )
        >>> passed
        True
        >>> evidence["match_score"]
        1.0
        """
        ...

    def register_source(self, name: str, config: Dict[str, Any]) -> None:
        """Dynamically register a new external verification source.

        Parameters
        ----------
        name : str
            Unique source identifier (e.g., 'store_api', 'hr_db').
        config : dict
            Source configuration: type (api/sqlite/static), URL/path,
            auth method, optional TTL.
        """
        ...
