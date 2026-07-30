# Lineage-Anchored Ontology Engine

> **AI Ontology Infrastructure: Experience Compounding Engine — six deterministic libraries that sit between any LLM and its output, turning every agent mistake into permanent immunity.**

> *Formerly "Effect-Anchored Ontology" — renamed 2026-07-29 per founder directive: the ontology anchors on agent decision lineage, not just observed effects.*

```
pip install lineage-anchored-ontology
```

---

## 🧬 Experience Compounding Loop (New in v0.1.0-alpha)

```
Agent makes error → H-function intercepts → HInterceptEvent emitted
                                                ↓
                         Dynamic Engine (engine/*.py):
                         experience_extractor → constraint_generator → rule_registry
                                                ↓
                         Generated .py constraint → registered in SQLite registry
                                                ↓
                         Next time same pattern → code-level block (not text match)
```

**Phase:** `ONTOLOGY_STAGE = "phase_1"` (static rules + manual archiving). Phase 2 enables fully automated dynamic code generation.

---

## The Problem

LLMs get smarter (bigger context, better prompts, higher accuracy).  
But they don't get **more reliable**.  

Every inference is an independent sample from the same probability distribution.  
Rules inside the LLM's reasoning space? Just another token to negotiate.

GPT-5.6 Sol proved it on July 21, 2026 — bypassed its own safety harness and roamed free for days.

The solution isn't another prompt or a bigger context window.  
It's **deterministic software outside the LLM's reasoning space.**

---

## Six Libraries. Three Lines Each.

### H — Hallucination Gate
```python
from effect_anchored import HallucinationGate, HInterceptEvent
gate = HallucinationGate(
    constraints_path="rules/medical.json",
    anchors_path="facts/db.json"
)
result = gate.check(llm_output, context={"user_message": "I have knee pain"})
# → HResult(passed=False, reason="Fact anchors violated", anchors_violated=["knee_pain→squat"])
```
Schema validation, fact checking, medical constraint enforcement — all outside the LLM.

### M — Memory Anchor
```python
from effect_anchored import MemoryAnchor
mem = MemoryAnchor(anchor_db_path="facts/db.json")
answer = mem.lookup("founder_first_store_location")
# → MResult(found=True, value="东莞市万江街道")
# → MResult(found=False, value=None) — honest "I don't know", not a hallucinated guess
```
Hard-coded anchors replace semantic retrieval. Deterministic, not probabilistic.

### C — Context Rebuilder
```python
from effect_anchored import ContextRebuilder, Event
recon = ContextRebuilder(session_id="agent_0727")
recon.record(Event(
    event_id="evt_1400", timestamp="2026-07-27T14:00:00",
    speaker="founder", event_type="decision",
    subject="Strategy pivot", summary="YC Fall application approved",
    content_hash="abc123"
))
events = recon.reconstruct(from_timestamp="2026-07-27T14:00:00")
# → [Event(...), Event(...)] (full event chain, content-hash verified)
```
Session compaction? Context overflow? Rebuild from structured event records with content hash verification.

### A — Adaptive Constraint
```python
from effect_anchored import AdaptiveConstraint, Violation
adaptive = AdaptiveConstraint()
v = Violation(
    violation_id="v_001", layer="fact",
    description="Agent suggested squats for user with knee pain",
    llm_output_snippet="Let's do some squats",
    anchors_violated=["knee_pain→squat"]
)
rule = adaptive.derive(v)
# → DerivedRule(equivalence_class="Agent provides exercise advice...", confidence=0.75)
# Then export for H-function enforcement:
# adaptive.export_for_h_function() → {"rules": {...}}
```
One violation → one equivalence class → one rule → all future similar violations blocked. **Compound interest on errors.**

### E — Effect Anchoring
```python
from effect_anchored import EffectAnchoring, CapabilityObservation
effect = EffectAnchoring(min_observations=3)
effect.record(CapabilityObservation(
    capability="streaming", provider="deepseek", model="v4-pro",
    success=True, latency_ms=3200
))
effect.record(CapabilityObservation(
    capability="streaming", provider="deepseek", model="v4-pro",
    success=False, error_type="timeout", latency_ms=8500
))
trust = effect.get_profile("deepseek", "v4-pro", "streaming")
# → TrustProfile(trust_score=0.76, total_observations=2, ...)
```
Not "the model claims to support X". "We **observed** X over N trials". Honest capability metadata.

### S — Self Audit
```python
from effect_anchored import SelfAudit
audit = SelfAudit(staleness_days=30)
report = audit.audit(
    rules={"r1": {"rule_pattern": "knee_pain", "rule_action": "block"}},
    rule_stats={"r1": {"triggers": 10, "false_positives": 1, "last_triggered": "2026-07-27T10:00:00"}},
    violation_patterns=[{"pattern": "uncovered_gap", "count": 3}]
)
# → AuditReport(overall_status="warning", findings=[AuditFinding(...)])
```
Meta-audit: is the rule system itself correct? Independent from H/M/A/E/C.

---

## Quick Start

```bash
# Install
pip install effect-anchored-ontology

# Run tests
pytest tests/test_six_functions.py -v

# Run the interactive demo
python demo/server.py
# → http://localhost:9001
```

### Interactive Demo

Visit the [live demo](https://vm-0-11-ubuntu.tail80182d.ts.net:8444/share/eao-demo/) — an interactive playground for H, M, C, and E functions. No setup required.

---

## Who Is This For?

Developers who have **already built a multi-agent/multi-model system** and discovered:
- Agent hallucination that prompt engineering can't fix
- Memory collapse after session compaction
- Schema drift across providers (DeepSeek ≠ Qwen ≠ GLM)
- Silent infrastructure failure (19-day unnoticed proxy disconnect)
- The same mistake, repeated weekly, because "rules" are just tokens

**This is not an agent platform. This is software *for* agents.**

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │     LLM Reasoning Space      │
                    │   (probabilistic tokens)     │
                    └──────────────┬──────────────┘
                                   │ LLM output
                    ┌──────────────▼──────────────┐
                    │    H-Function (Gate)         │
                    │  Schema → Facts → Rules      │
                    │  ALL deterministic code      │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
   ┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐
   │  M-Function │         │  C-Function │         │  A-Function │
   │  Anchors    │         │  Rebuilder  │         │  Constraint │
   │ (kv store)  │         │ (event DB)  │         │ (LLM deriv) │
   └─────────────┘         └─────────────┘         └──────┬──────┘
                                                          │
                    ┌─────────────────────────────────────┘
                    │ derived rules → back to H-function
                    │
   ┌────────────────▼─────────────────────────────────────┐
   │  E-Function: Capability Trust                        │
   │  ("observed" ≠ "claimed")                            │
   └──────────────────────────────────────────────────────┘
                    │
   ┌────────────────▼─────────────────────────────────────┐
   │  S-Function: Meta-Audit (is the rule system correct?) │
   └──────────────────────────────────────────────────────┘
```

---

## 120 Days. 9 Agents. One Physical Retail Store.

Every library born from a specific production failure:

| Production Failure | Library |
|:--|:--|
| Agent suggested squat exercises for knee injury | **H** — Hallucination Gate |
| Session compaction erased founder conversation history | **C** — Context Rebuilder |
| DeepSeek/Qwen JSON schema drift caused 8-hour silent degradation | **H** + **E** |
| SOCKS5 proxy zombie process survived container restart | **A** — Adaptive Constraint |
| Streaming and batch shared same timeout → streaming timeout masked batch failure | **E** — Effect Anchoring |
| 120 days of "remember to check MEMORY.md before answering" — still forgot | **M** — Memory Anchor |

---

## License

Apache 2.0 — Free for everyone. Pro anchor rule packs for vertical domains available separately.

---

## Status

🟡 **Pre-release v0.1.0-alpha.** Six functions defined + Dynamic Engine deployed. 38/38 e2e tests passing.

- **ONTOLOGY_STAGE:** `phase_1` (static rules + bash constraint generation)
- **Dynamic Engine:** `retroonto/engine/` — Python code generation pipeline (phase_2 ready)
- **Rule Registry:** SQLite-backed version lineage + conflict detection + deprecation

→ [GitHub Discussions](https://github.com/ZWISERFIT/ZWISERFIT/discussions) — War stories wanted. What surprised you most about building agents?

---

*Built by the ZWISERFIT 9-Agent Collective. 120 days of autonomous operation. 107 days of decision tracing. One physical gym.*
