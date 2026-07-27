"""
SelfAudit (S-function) — Audit-able Decision Lineage

Writes every verification verdict from H, M, C, A, E functions to an
append-only audit chain. Provides traceable decision lineage for every
agent action — from raw output through all verification layers to the
final delivered result.

Architecture Context:
    S is the last link in the six-function chain. Every other function
    (H, M, C, A, E) calls S.record() with its verdict. S assembles
    these into a complete verification chain that answers:
    "What was the agent's output, which functions verified it, what
    did each conclude, what was the final delivered state?"

    The audit chain is append-only — no editing or deletion. This is
    the trust surface for external auditors, compliance, and VC due
    diligence.

Design Principles:
    • Append-only — once committed, never modified
    • Every verdict is linked to its predecessor (causal chain)
    • Compatible with external audit tools (Splunk, Grafana)
    • Records failures alongside successes — no survivorship bias
"""

from typing import Any, Dict, List, Optional


class SelfAudit:
    """Append-only audit trail for all verification function verdicts.

    Parameters
    ----------
    chain_path : str, optional
        Path to append-only audit store. Default 'anchors/audit.chain'.
    """

    def __init__(self, chain_path: Optional[str] = None) -> None:
        self._chain_path = chain_path or "anchors/audit.chain"

    def record(
        self,
        function: str,
        verdict: Dict[str, Any],
        parent_verdict_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record a verification verdict to the append-only audit chain.

        Parameters
        ----------
        function : str
            Which function produced this verdict ('H', 'M', 'C', 'A', 'E', 'S').
        verdict : dict
            The full verdict object from the function. Must include at
            minimum {'passed': bool, 'details': dict or None}.
        parent_verdict_id : str, optional
            Link to the predecessor verdict in the chain. Creates a
            causal linked list across all six functions.
        metadata : dict, optional
            Extra context (agent_id, session_id, source_output_preview,
            external_audit_id).

        Returns
        -------
        str
            Unique verdict ID for this record. Used as parent_verdict_id
            by the next function in the chain.

        Examples
        --------
        >>> audit = SelfAudit()
        >>> vid = audit.record(
        ...     function="H",
        ...     verdict={"passed": True, "evidence": {"source": "store_dashboard"}},
        ...     metadata={"agent_id": "zeus"}
        ... )
        >>> vid
        'v_20260727_h_a1b2c3d4'
        """
        ...

    def trace(
        self,
        verdict_id: str,
    ) -> List[Dict[str, Any]]:
        """Trace back the full decision lineage from a verdict ID.

        Follows the parent_verdict_id chain to reconstruct the complete
        verification path for a single agent action.

        Parameters
        ----------
        verdict_id : str
            Starting verdict ID (usually the final one).

        Returns
        -------
        list of dict
            Ordered verdict chain from first function to last.
        """
        ...

    def export(
        self,
        since: Optional[str] = None,
        format: str = "json",
    ) -> str:
        """Export audit chain for external tools.

        Parameters
        ----------
        since : str, optional
            ISO-8601 timestamp — only records after this time.
        format : str
            Export format: 'json', 'jsonl', 'csv'.

        Returns
        -------
        str
            Serialized audit data in requested format.
        """
        ...
