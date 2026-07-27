"""
EffectAnchoring (E-function) — Observed Effect Recording

Records observed effects from provider interactions with honest
capability metadata. Not a benchmark — a production observability log
that tracks what actually happens when an agent calls a provider.

Architecture Context:
    E sits between the agent's provider call and the response handling.
    For every interaction, it records:
    - Provider identity and model variant
    - Mode (streaming, batch, tool-call)
    - Observed latency (connect, first-byte, total)
    - Success/failure (and failure mode)
    - Schema compatibility report

    This data feeds into A (AdaptiveConstraint) for rule derivation
    and gives operators honest provider-level capability metadata —
    not vendor-reported specs, but observed ground truth.

Design Principles:
    • Records what ACTUALLY happened, not what was supposed to happen
    • Honest metadata — no pretending all providers have identical semantics
    • Effect data is append-only — never overwrite a recorded observation
    • Streaming and batch effects are recorded separately
"""

from typing import Any, Dict, List, Optional


class EffectAnchoring:
    """Records observed provider effects with honest capability metadata.

    Parameters
    ----------
    store_path : str, optional
        Path to effect store (SQLite or JSONL). Default 'anchors/effects.registry'.
    """

    def __init__(self, store_path: Optional[str] = None) -> None:
        self._store_path = store_path or "anchors/effects.registry"

    def record(
        self,
        provider: str,
        mode: str,
        observed_latency_ms: int,
        success_rate: float,
        failure_mode: Optional[str] = None,
        schema_compatibility: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record an observed provider effect.

        Parameters
        ----------
        provider : str
            Provider identifier (e.g., 'deepseek_v4', 'qwen-plus').
        mode : str
            Interaction mode: 'streaming', 'batch', 'tool_call',
            'structured_output'.
        observed_latency_ms : int
            Total observed latency in milliseconds.
        success_rate : float
            0.0 to 1.0 — fraction of calls in this recording window
            that completed successfully.
        failure_mode : str, optional
            If not 1.0, describe the dominant failure mode
            (e.g., 'timeout', 'schema_mismatch', 'auth_error').
        schema_compatibility : dict, optional
            Report of schema compatibility: {
                'expected': 'tools', 'actual': 'functions',
                'compatible': False, 'mapped_via': 'schema_adapter'
            }
        metadata : dict, optional
            Extra context (agent_id, prompt_hash, model variant).

        Returns
        -------
        str
            Effect record ID for cross-referencing with audit log.

        Examples
        --------
        >>> effect = EffectAnchoring()
        >>> effect.record(
        ...     provider="deepseek_v4",
        ...     mode="streaming",
        ...     observed_latency_ms=3200,
        ...     success_rate=0.94
        ... )
        'eff_20260727_a1b2c3'
        """
        ...

    def query(
        self,
        provider: Optional[str] = None,
        mode: Optional[str] = None,
        since: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query recorded effects, optionally filtered.

        Parameters
        ----------
        provider : str, optional
            Filter by provider.
        mode : str, optional
            Filter by mode.
        since : str, optional
            ISO-8601 timestamp — only records after this time.

        Returns
        -------
        list of dict
            Matching effect records.
        """
        ...

    def summarize(self, provider: str) -> Dict[str, Any]:
        """Get a summary of provider capability from all recorded effects.

        Parameters
        ----------
        provider : str
            Provider identifier.

        Returns
        -------
        dict
            Aggregated capability metadata with mean/p95 latency,
            success rate, dominant failure modes, mode coverage.
        """
        ...
