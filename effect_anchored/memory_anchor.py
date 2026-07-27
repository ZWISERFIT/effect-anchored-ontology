"""
MemoryAnchor (M-function) — Hard-Coded Retrieval Anchors

Stores terminal-state facts as immutable retrieval anchors that
cannot be overridden by token probabilities in the LLM inference space.

Architecture Context:
    M runs as a separate process with its own storage (SQLite).
    Every agent query passes through M before hitting semantic search:
        1. Exact anchor match → return anchor value (deterministic)
        2. No anchor → fall through to semantic/vector search (probabilistic)
        3. Both miss → return "unknown" (no guessing)

    An anchor is a key-value pair where the VALUE is authoritatively
    true at the time of anchoring. The KEY is a normalized identifier.

Design Principles:
    • Anchors are outside the LLM's token space
    • Anchors can have TTL (time-to-live) for facts that decay
    • Anchor updates require explicit invalidation, not LLM agreement
    • Exact match only — no semantic matching on keys
"""

from typing import Any, Dict, Optional, Tuple


class MemoryAnchor:
    """Stores and retrieves hard-coded factual anchors outside LLM space.

    Parameters
    ----------
    db_path : str, optional
        Path to SQLite database for anchor storage. Defaults to
        'anchors/facts.db' relative to project root.
    ttl_default : int, optional
        Default time-to-live in seconds (0 = no expiry). Default 86400.
    """

    def __init__(self, db_path: Optional[str] = None, ttl_default: int = 86400) -> None:
        self._db_path = db_path or "anchors/facts.db"
        self._ttl_default = ttl_default

    def get(self, key: str) -> Tuple[bool, Optional[Any]]:
        """Retrieve an anchor value by exact key match.

        Looks up KEY in the anchor database. Returns the value only
        on exact match. No fuzzy matching, no semantic similarity.

        Parameters
        ----------
        key : str
            Normalized anchor key. Must match exactly.
            Example: "zwf.store_count" or "a16z.tracker_status"

        Returns
        -------
        (bool, value or None)
            - (True, value) if exact match found and anchor is valid
            - (False, None) if no anchor or anchor expired

        Examples
        --------
        >>> anchor = MemoryAnchor()
        >>> found, val = anchor.get("zwf.store_count")
        >>> found
        True
        >>> val
        1
        """
        ...

    def set(
        self,
        key: str,
        value: Any,
        source: str = "manual",
        ttl: Optional[int] = None,
    ) -> bool:
        """Set an anchor with a hard-coded value.

        Parameters
        ----------
        key : str
            Normalized anchor key.
        value : any
            The authoritative value (must be JSON-serializable).
        source : str, optional
            Origin of the fact (e.g., 'founder', 'store_db', 'audit').
        ttl : int, optional
            Custom TTL in seconds. None uses default.

        Returns
        -------
        bool
            True if set successfully, False on error.
        """
        ...

    def invalidate(self, key: str) -> bool:
        """Mark an anchor as expired, forcing fallback to semantic search.

        Parameters
        ----------
        key : str
            Anchor key to invalidate.

        Returns
        -------
        bool
            True if anchor found and invalidated.
        """
        ...

    def search(self, query: str, fuzzy: bool = True) -> Dict[str, Any]:
        """Search anchors by normalized key patterns (for debugging/admin).

        Parameters
        ----------
        query : str
            Key pattern to search (supports wildcard: 'zwf.*').
        fuzzy : bool
            Enable fuzzy key matching for admin/override lookups.

        Returns
        -------
        dict
            Matching anchor entries with key, value, source, created_at.
        """
        ...
