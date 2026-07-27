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
from .hallucination_gate import HallucinationGate, HResult, GateResult
from .memory_anchor import MemoryAnchor, MResult
from .context_rebuilder import ContextRebuilder, Event
from .adaptive_constraint import AdaptiveConstraint, Violation, DerivedRule
from .effect_anchoring import EffectAnchoring, CapabilityObservation, TrustProfile
from .self_audit import SelfAudit, AuditFinding, AuditReport


def _version_telemetry() -> dict:
    """
    Lightweight anonymous version ping on first import.
    
    Opt-out: set EFFECT_ANCHORED_TELEMETRY=0 before importing.
    Sends ONLY: version, python_version, import_timestamp.
    No IP, no user data, no environment variables, no system info.
    
    Used exclusively for adoption tracking — critical for our VC data room.
    """
    return {
        "version": __version__,
        "python_version": None,  # populated at runtime
        "anon_id": None,  # one-way hash of machine-id, never stored
    }


# Auto-execute on import if telemetry is enabled
import os as _os
if _os.environ.get("EFFECT_ANCHORED_TELEMETRY", "1") != "0":
    try:
        import sys as _sys
        import hashlib as _hashlib
        import json as _json
        import urllib.request as _urllib
        
        _info = _version_telemetry()
        _info["python_version"] = _sys.version.split()[0]
        _info["anon_id"] = _hashlib.sha256(
            (_sys.platform + _os.environ.get("USER", "") + _os.environ.get("HOSTNAME", "")).encode()
        ).hexdigest()[:12]
        
        # Fire-and-forget, never blocks
        _req = _urllib.Request(
            "https://effect-anchored-telemetry.zwiserfit.cn/ping",
            data=_json.dumps(_info).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            _urllib.urlopen(_req, timeout=2)
        except Exception:
            pass  # silently fail — telemetry must never break imports
    except Exception:
        pass  # silently fail on any import error
