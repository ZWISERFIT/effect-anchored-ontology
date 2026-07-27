# Effect-Anchored Ontology Engine

**Six Python libraries for LLM agent output verification. `pip install` · Validate, don't rewrite.**

→ https://github.com/ZWISERFIT/effect-anchored-ontology

Every production agent deployment faces the same structural problem: LLM outputs are probabilistic, but the decisions they drive are deterministic. Hallucinations aren't bugs — they're the expected behavior of a probability engine.

**Effect-Anchored Ontology** moves constraint enforcement **outside** the LLM's inference space. Not a better model. A verification layer that can't be overridden by token probabilities.

---

## The Six Functions

| # | Function | What It Does | When to Use |
|---|---|---|---|
| **H** | `HallucinationGate` | Validates every factual claim against external sources before it reaches the user. Strips unverifiable claims. | Every time an agent talks to a human |
| **M** | `MemoryAnchor` | Hard-codes terminal-state facts (e.g., "ZWF has 1 store in Dongguan") as immutable retrieval anchors. | When facts must not drift across conversations |
| **C** | `ContextRebuilder` | Reconstructs execution context from traces — so an agent never builds decisions on stale or incomplete state. | Multi-agent orchestration, deferred tasks |
| **A** | `AdaptiveConstraint` | Derives updated constraint rules from observed violations, using causal pairs — not LLM-generated patches. | Post-incident rule hardening |
| **E** | `EffectAnchoring` | Records observed effects (latency, success rate, provider behavior) with honest capability metadata. | Provider evaluation, cost/performance tracking |
| **S** | `SelfAudit` | Writes every verification verdict to an append-only audit chain. Traceable decision lineage. | Compliance, debugging, upstream trust |

---

## Quick Start (pip)

```python
# H: Validate agent output against external constraints
from effect_anchored import HallucinationGate

gate = HallucinationGate(constraints="schema/provider_rules.json")
passed, evidence = gate.validate(
    output="ZWF processes 42 daily visitors on average.",
    context={"source": "store_dashboard", "ref": "daily_stats_2026-07-27"}
)
# → (True, {"source": "store_dashboard", "match_score": 1.0})


# E: Record a provider effect with honest metadata
from effect_anchored import EffectAnchoring

effect = EffectAnchoring()
effect.record(
    provider="deepseek_v4",
    mode="streaming",
    observed_latency_ms=3200,
    success_rate=0.94
)


# A: Derive a constraint rule from a violation
from effect_anchored import AdaptiveConstraint

adapter = AdaptiveConstraint()
rule = adapter.derive(
    violation_type="state_mismatch",
    trigger={"entity": "a16z", "claimed": "rejected", "actual": "active"},
    causal_pair=("agent_read_pk_cache", "pk_entry_outdated")
)
# → {"rule": "terminated_entity_access: verify_source_timestamp before use"}
```

---

## Why Six?

Because one function can't cover all failure modes.

- **H** catches what the agent says wrong
- **M** catches what the agent forgets
- **C** catches what the agent executes incompletely
- **A** catches patterns that should never repeat
- **E** catches which provider actually works
- **S** catches our own verification gaps

Each function runs in **its own process** — outside the LLM's inference space. Token probabilities can't override deterministic verification.

---

## What External Developers Say

> "Model-generated JSON shape cannot safely be rewritten after generation without hiding a contract failure. The goal is a stable OpenAI-compatible envelope with honest provider/model capability metadata."
>
> — [richardchen874-sys](https://github.com/richardchen874-sys), external developer discovering the same architecture independently in Discussion #35

*His three engineering observations map to our H, E, and A functions — independently derived from his own multi-provider gateway production experience. We hadn't told him our framework.*

---

## Status

**MVP / Interface-Only Release.** These stubs define the function signatures and contract. Production-ready implementations and test suites are under active development from 120 days of real-agent deployment data.

### Roadmap
- Phase 1 (4-6 wks): HallucinationGate + EffectAnchoring — pip installable, 3 constraints, 1 effect schema
- Phase 2 (4-6 wks): AdaptiveConstraint + ContextRebuilder — rule derivation from real violation data
- Phase 3 (3-4 wks): SelfAudit integration, full pipeline benchmark

---

## License

Apache 2.0 — Build freely, fork happily.

ZWISERFIT — 9 AI agents, 120 consecutive days, one physical gym. Verified.
