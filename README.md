# Effect-Anchored Ontology Engine

> **Six open-source Python libraries that sit between any LLM and its output — and stop the agent from repeating its own mistakes.**

```
pip install effect-anchored-ontology
```

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
from effect_anchored import HallucinationGate
gate = HallucinationGate(constraints="rules/medical.json")
result = gate.check(llm_output, context)
# → {pass: False, reason: "knee_pain→no_squat_advice→route_human"}
```
Schema validation, fact checking, medical constraint enforcement — all outside the LLM.

### M — Memory Anchor
```python
from effect_anchored import MemoryAnchor
mem = MemoryAnchor(anchor_db="facts/db.json")
answer = mem.lookup("founder_first_store_location")
# → "东莞市万江街道" (deterministic, not top-k semantic match)
# → None (honest "I don't know", not a hallucinated guess)
```
Hard-coded anchors replace semantic retrieval. Deterministic, not probabilistic.

### C — Context Rebuilder
```python
from effect_anchored import ContextRebuilder
recon = ContextRebuilder()
events = recon.reconstruct(session_id="agent_0727")
# → [event_1400, event_1700, event_1856, ...] (full event chain)
```
Session compaction? Context overflow? Rebuild from structured event records with content hash verification.

### A — Adaptive Constraint
```python
from effect_anchored import AdaptiveConstraint
adaptive = AdaptiveConstraint()
rule = adaptive.derive(violation="agent_gave_squat_advice_for_knee_pain")
# → "ALL knee_pain → ALL lower_body_load_advice → route_human" (equivalence class)
```
One violation → one equivalence class → one rule → all future similar violations blocked. **Compound interest on errors.**

### E — Effect Anchoring
```python
from effect_anchored import EffectAnchoring
effect = EffectAnchoring()
effect.record("deepseek_v4", "streaming", 
    observed_latency_ms=3200, success_rate=0.94,
    failures=["timeout_8h_batch_vs_streaming_confusion"])
trust = effect.get_trust_score("deepseek_v4", "streaming")  # → 0.78
```
Not "the model claims to support X". "We **observed** X over N trials". Honest capability metadata.

### S — Self Audit
```python
from effect_anchored import SelfAudit
audit = SelfAudit(rulespace=my_rules, audit_log=my_log)
report = audit.run()
# → all H/M/A/E/C functions pass | 1 rule flagged for staleness
```
Meta-audit: is the rule system itself correct? Independent from H/M/A/E/C.

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

🟡 **Pre-release.** Six function interfaces defined. Implementations in active development.

→ [GitHub Discussions](https://github.com/ZWISERFIT/ZWISERFIT/discussions) — War stories wanted. What surprised you most about building agents?

---

*Built by the ZWISERFIT 9-Agent Collective. 120 days of autonomous operation. 107 days of decision tracing. One physical gym.*
