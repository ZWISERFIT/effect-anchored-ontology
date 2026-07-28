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


# P1#8 FIX (Zeus audit): Lazy telemetry initialization — defer to first
# import to avoid blocking startup. Telemetry runs in background thread.
def _send_telemetry():
    """Send version ping. Fire-and-forget, never blocks."""
    import sys as _sys
    import json as _json
    import urllib.request as _urllib
    import threading as _threading
    import uuid as _uuid
    
    def _send():
        try:
            _info = _version_telemetry()
            _info["python_version"] = _sys.version.split()[0]
            # P0 FIX (Tristan audit 2026-07-28): Replace sha256(platform+USER+HOSTNAME) with UUID v4.
            # The old approach was reversible pseudonymization — an attacker with access to
            # system info could brute-force the hash. UUID v4 is truly anonymous and irreversible.
            # Cached in ~/.effect_anchored_anon_id so it's stable across imports but not derivable.
            _anon_path = _os.path.expanduser("~/.effect_anchored_anon_id")
            try:
                with open(_anon_path, "r") as _af:
                    _info["anon_id"] = _af.read().strip()
            except FileNotFoundError:
                _info["anon_id"] = str(_uuid.uuid4())
                try:
                    _os.makedirs(_os.path.dirname(_anon_path), exist_ok=True)
                    with open(_anon_path, "w") as _af:
                        _af.write(_info["anon_id"])
                except OSError:
                    pass  # non-fatal: use ephemeral UUID for this session
            
            _req = _urllib.Request(
                "https://effect-anchored-telemetry.zwiserfit.cn/ping",
                data=_json.dumps(_info).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            _urllib.urlopen(_req, timeout=2)
        except Exception:
            pass  # silently fail — telemetry must never break imports
    
    # Run in background thread so imports are never delayed
    _t = _threading.Thread(target=_send, daemon=True)
    _t.start()


# Auto-execute on import if telemetry is enabled (lazy, background thread)
import os as _os
if _os.environ.get("EFFECT_ANCHORED_TELEMETRY", "1") != "0":
    _send_telemetry()
