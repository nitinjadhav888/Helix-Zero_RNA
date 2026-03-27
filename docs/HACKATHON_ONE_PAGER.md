# Helix-Zero Hackathon One-Pager

## 1) Objective (Simple)
We are building an AI pipeline that designs RNA "smart pesticides":
- lethal to target pest genes,
- safer for non-target organisms,
- and chemically optimized for stability in the real world.

In plain terms: this is a software-first platform that finds high-quality RNA candidates faster than trial-and-error lab screening.

## 2) Problem We Solve
Traditional RNA candidate discovery has three hard bottlenecks:
- Too many combinations to test manually.
- Safety screening is expensive and slow.
- Good molecules often fail later due to instability.

Our app solves this in one flow:
- generate candidate RNAs,
- score safety and efficacy,
- optimize chemical modifications,
- and return an explainable ranked shortlist.

## 3) What We Built (End-to-End)
Pipeline endpoint: `POST /api/pipeline/e2e`

It performs:
1. Candidate generation from target sequence.
2. Multi-layer biosafety and homology checks.
3. Objective-based ranking (balanced / safety / efficacy / essentiality).
4. Chemical modification simulation (2'-OMe, 2'-F, PS).
5. Optional enrichment from deep-learning backend.

Primary app stack:
- Flask orchestration API (`web_app/app.py`)
- Core RNA engine (`web_app/engine.py`)
- Chemical simulation + AI optimizer (`web_app/chem_simulator.py`)
- Essentiality scoring (`web_app/essentiality.py`)
- DL backend proxy (`backend/main.py`)

## 4) Our Moat (Why This Is Defensible)
### Product Moat
- One-click E2E flow instead of disconnected scripts.
- Built-in explainability (scores + warnings + rationale).
- Demo-ready API for quick integration with dashboards.

### Technical Moat
- Multi-layer safety filtering integrated before ranking.
- Objective-aware ranking strategy (not single-metric sorting).
- Combined chemical and sequence-level optimization.
- Modular architecture for fast iteration during hackathon.

### Data/Knowledge Moat
- Uses curated rules and evidence-backed scoring features already encoded in the system.
- Integrates public scientific principles (thermodynamics, RNAi design rules, off-target heuristics) into actionable software.

## 5) Uniqueness
Most projects do only one piece (either sequence scoring, or structure, or chemistry).
Helix-Zero combines all three in one production-style pipeline:
- sequence design,
- safety firewall,
- chemistry optimization,
- and deployment-ready API outputs.

## 6) Demo Script (4-5 Minutes)
1. Send `targetSequence`, `nonTargetSequence`, `geneName` to `/api/pipeline/e2e`.
2. Show candidate count and top ranked sequence.
3. Show safety score and efficacy score.
4. Show chemical modification recommendation and therapeutic index.
5. Show final top 5 candidates for decision support.

## 7) Judge-Friendly Value Statement
"We are not replacing biology experts. We are giving them a decision engine that shortens discovery cycles, reduces unsafe candidates early, and increases confidence before lab validation."

## 8) Online Research Snapshot (Used for Framing)
We cross-checked positioning with public research themes:
- RNAi therapeutics maturity and translational challenges (delivery, off-target, stability).
- Transformer attention relevance for sequence modeling.

Representative sources used:
- Vaswani et al., "Attention Is All You Need" (arXiv:1706.03762).
- Internal project references in CMS and v7/v8 docs (Setten 2019, Bramsen 2009, Ui-Tei 2004, Mathews 2004).

## 9) What Is Next (Post-Hackathon)
- Attach Helix_Zero1 advanced CMS as dedicated module service.
- Add one-click PDF report export for judges/investors.
- Add benchmark suite against baseline rule-only rankers.
