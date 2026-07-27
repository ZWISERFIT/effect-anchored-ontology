"""
Effect-Anchored Ontology Engine
================================

Six deterministic libraries that operate outside the LLM's reasoning space.

Functions:
    H - HallucinationGate: schema/fact validation, outside LLM probability space
    M - MemoryAnchor: hard-coded anchor retrieval, deterministic (not semantic)
    C - ContextRebuilder: structured event recording + post-compaction reconstruction
    A - AdaptiveConstraint: violation → equivalence class → rule generation
    E - EffectAnchoring: capability trust scoring from observed effects (not model claims)
    S - SelfAudit: meta-audit of the rule system itself

Built from 120 days of 9-agent autonomous operation in a physical retail store.
"""

__version__ = "0.1.0-alpha"
__all__ = [
    "HallucinationGate",
    "MemoryAnchor",
    "ContextRebuilder",
    "AdaptiveConstraint",
    "EffectAnchoring",
    "SelfAudit",
]
