# Helix-Zero V8 :: Complete Technical Documentation
## Regulatory-Grade RNA Interference Design Engine

**Version:** 8.0  
**Date:** March 2026  
**Status:** Production Ready  

---

# Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Scientific Theory](#3-scientific-theory)
4. [V6 Model: 9-Layer Bio-Safety Firewall](#4-v6-model-9-layer-bio-safety-firewall)
5. [V7 Model: Deep Learning Foundation](#5-v7-model-deep-learning-foundation)
6. [V8 Advanced Features](#6-v8-advanced-features)
7. [API Reference](#7-api-reference)
8. [Data Flow Diagrams](#8-data-flow-diagrams)
9. [Implementation Details](#9-implementation-details)
10. [Testing Guide](#10-testing-guide)

---

# 1. Executive Summary

## What is Helix-Zero?

Helix-Zero is a **computational platform for designing RNA interference (RNAi) triggers** - molecules that can silence specific genes in pests without harming beneficial organisms like honeybees.

## Key Problem It Solves

When designing pesticides that use RNAi:
1. **Efficacy**: The siRNA must effectively silence the target pest gene
2. **Safety**: The siRNA must NOT silence any genes in non-target organisms (pollinators)
3. **Optimization**: The siRNA must be chemically stable for practical use

## Solution

Helix-Zero uses a **multi-layered approach** combining:
- Thermodynamic calculations (SantaLucia 1998 nearest-neighbour model)
- Machine learning (RiNALMo-v2 Transformer)
- Bioinformatic filtering (Bloom filters, homology search)
- Chemical simulation (2'-OMe, 2'-F, PS modifications)

---

# 2. Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     HELIX-ZERO V8 ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   FLASK      │    │   FASTAPI    │    │   FRONTEND   │     │
│  │   (V6)      │◄──►│   (V7)       │◄──►│   (UI)       │     │
│  │   Port 5000  │    │   Port 8000  │    │   Browser    │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│        │                   │                                    │
│        ▼                   ▼                                    │
│  ┌──────────────┐    ┌──────────────┐                        │
│  │ 9-Layer      │    │ RiNALMo-v2    │                        │
│  │ Safety       │    │ Transformer    │                        │
│  │ Firewall     │    │ Neural Net     │                        │
│  └──────────────┘    └──────────────┘                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SUPPORTING MODULES                      │   │
│  ├─────────────┬─────────────┬─────────────┬──────────────┤   │
│  │ Bloom Filter│ Essentiality│ Chem        │ RNA          │   │
│  │ (O(1)      │ Scoring     │ Simulator   │ Accessibility│   │
│  │  Homology)  │ (DEG/OGEE)  │ (AI)        │ (Thermodyn) │   │
│  └─────────────┴─────────────┴─────────────┴──────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    DATA STORAGE                           │   │
│  ├─────────────┬─────────────┬─────────────────────────────┤   │
│  │ SQLite DB   │ JSON DBs   │ Session State                │   │
│  │ (History)   │ (Genes)    │ (JavaScript)                │   │
│  └─────────────┴─────────────┴─────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology | Port | Purpose |
|-----------|------------|------|---------|
| Web Server | Flask | 5000 | Main application, V6 pipeline |
| ML Backend | FastAPI + PyTorch | 8000 | RiNALMo-v2 predictions |
| Frontend | HTML + Bootstrap + jQuery | - | User interface |
| Database | SQLite | - | Sequence history storage |
| Genome Index | Bloom Filter | - | O(1) homology search |

## File Structure

```
Helix-Zero6.0/
├── web_app/
│   ├── app.py              # Flask main application (5000)
│   ├── engine.py           # V6 9-layer safety engine
│   ├── essentiality.py     # Gene essentiality scoring
│   ├── bloom_filter.py     # O(1) genome indexing
│   ├── chem_simulator.py   # Chemical modification AI
│   ├── rna_accessibility.py # Thermodynamic accessibility analysis
│   ├── rna_structure.py    # 2D Structure prediction (Nussinov fallback)
│   ├── vienna_integration.py # NEW! ViennaRNA (RNAfold) integration
│   ├── svg_generator.py    # 2D SVG visualization
│   ├── pdb_generator.py    # PDB 3D structure generation
│   ├── tissue_transcriptomics.py # Tissue-specific filtering
│   ├── models.py           # SQLAlchemy database models
│   ├── rag_agent.py        # RAG explanation agent
│   ├── templates/
│   │   └── index.html     # Main UI template
│   └── static/
│       ├── script.js        # Frontend JavaScript
│       ├── style.css       # Styling
│       └── data/           # JSON databases
│           ├── essential_genes.json
│           ├── ogee_essentiality.json
│           ├── rnai_phenotypes.json
│           └── tissue_expression.json
├── backend/
│   └── main.py            # FastAPI ML server (8000)
│                            # Contains RiNALMo-v2 model
└── docs/
    └── [Documentation files]
```

---

# 3. Scientific Theory

## 3.1 RNA Interference (RNAi) Basics

### What is RNAi?

RNA interference is a natural cellular mechanism where short RNA molecules can "silence" specific genes. In pest control:

1. We design a small piece of RNA called **siRNA** (small interfering RNA)
2. This siRNA matches a critical gene in the pest
3. When the pest consumes the siRNA, it silences the target gene
4. The pest dies or becomes unable to function

### The siRNA Structure

```
siRNA Duplex (21 base pairs):

    5' ─────────────────────────────── 3'
         │                          │
         │   GUIDE STRAND           │
         │   (the one that guides) │
         │                          │
    3' ─────────────────────────────── 5'
         │                          │
         │   PASSENGER STRAND       │
         │   (discarded by RISC)    │
         └──────────────────────────┘

Position: 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21
          │  │  │  │  │  │  │  │  │  │   │  │  │  │  │  │  │  │  │  │  │
          ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼   ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼
         [A][T][G][G][A][C][T][A][C][A ][A ][G ][G ][A ][C ][G ][A ][C ][G ][A]
                                  ↑
                              SEED REGION
                             (positions 2-8)
                             Critical for target recognition
```

## 3.2 Thermodynamics: SantaLucia 1998 Nearest-Neighbour Model

### The Problem

DNA/RNA strands are held together by hydrogen bonds. The energy required to separate them is called **Free Energy (ΔG)**.

### The Solution

The SantaLucia 1998 model states: **"The stability of a base pair depends not just on itself, but also on its neighbour."**

### Base Pair Energies

Each dinucleotide pair has specific thermodynamic values:

| Dinucleotide | ΔH (kcal/mol) | ΔS (cal/mol·K) |
|--------------|---------------|-----------------|
| AA/TT        | -7.9         | -22.2          |
| AT           | -7.2         | -20.4          |
| TA           | -7.2         | -21.3          |
| GC           | -9.8         | -24.4          |
| CG           | -10.6        | -27.2          |

### Free Energy Calculation Formula

```
ΔG = ΔH - T × ΔS

Where:
- T = 310.15 K (37°C / body temperature)
- ΔH = Sum of all enthalpy values
- ΔS = Sum of all entropy values
```

### Example Calculation

For sequence "ATGC":
```
Step 1: Split into dinucleotides
- AT, TG, GC

Step 2: Look up values
- AT: ΔH = -7.2, ΔS = -20.4
- TG: ΔH = -8.5, ΔS = -22.7
- GC: ΔH = -9.8, ΔS = -24.4

Step 3: Sum values
- Total ΔH = -7.2 + (-8.5) + (-9.8) = -25.5
- Total ΔS = -20.4 + (-22.7) + (-24.4) = -67.5

Step 4: Calculate ΔG at 37°C
- ΔG = -25.5 - 310.15 × (-67.5 / 1000)
- ΔG = -25.5 + 20.9
- ΔG = -4.6 kcal/mol
```

### Why This Matters

| ΔG Value | Interpretation |
|----------|----------------|
| Very negative (< -30) | Very stable duplex |
| Moderate (-20 to -30) | Optimal for siRNA |
| Positive (> 0) | Unstable, won't form duplex |

## 3.3 The 15-Nucleotide Safety Rule

### The Critical Discovery

For effective RNAi-mediated gene silencing, a minimum of **15 contiguous nucleotides** of perfect complementarity is required between the siRNA and the target.

### The Safety Implication

```
If our siRNA has 15+ contiguous matches with a pollinator's genome:
→ It will silence that pollinator gene
→ This is LETHAL TO THE POLLINATOR
→ This candidate must be REJECTED
```

### How Helix-Zero Implements This

```
┌─────────────────────────────────────────────────────────────┐
│                    15-NT RULE CHECK                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  siRNA:    ATGGACTACAAGGACGACGA                              │
│              |||||||||||||||||  ← 15 contiguous matches     │
│  Bee Gene: ATGGACTACAAGGACGACGA                              │
│                                                              │
│  Result: REJECT ❌                                          │
│  Safety Penalty: -100 points                                 │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  siRNA:    ATGGACTACAAGGACGACGA                              │
│              |||||||||||    |||  ← Only 10 + 3 matches      │
│  Bee Gene: ATGGACTACAAGGAAAGCGCA                              │
│                                                              │
│  Result: PASS ✅ (not contiguous)                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 3.4 RISC Loading and Strand Selection

### What is RISC?

RISC (RNA-Induced Silencing Complex) is the cellular machinery that carries the siRNA and finds the target.

### The Strand Selection Problem

The siRNA duplex has two strands. RISC must select the **correct one** (guide strand) and discard the other (passenger strand).

### The Thermodynamic Solution

RISC naturally selects the strand whose **5' end is thermodynamically WEAKER**. This ensures proper guide strand selection.

```
┌─────────────────────────────────────────────────────────────┐
│                 STRAND ASYMMETRY                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GOOD (Positive Asymmetry):                                  │
│  5' end:  A-T-A-T  (weak, GC=0%)  ← RISC prefers THIS    │
│  3' end:  G-C-G-C  (strong, GC=100%)                       │
│  Asymmetry = +ΔG (GOOD)                                     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BAD (Negative Asymmetry):                                    │
│  5' end:  G-C-G-C  (strong, GC=100%)                       │
│  3' end:  A-T-A-T  (weak, GC=0%)  ← RISC prefers THIS     │
│  Asymmetry = -ΔG (BAD - wrong strand loaded)                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Asymmetry Formula

```
Asymmetry = Energy(3' end) - Energy(5' end)

Where:
- Positive = Good (5' end is weaker)
- Negative = Bad (5' end is stronger)
```

---

# 4. V6 Model: 9-Layer Bio-Safety Firewall

The V6 model is the **core safety engine** that evaluates each siRNA candidate against 9 different safety criteria.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 9-LAYER BIO-SAFETY FIREWALL                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐                                                │
│  │ Layer 1     │ GC Content Check (30-52% optimal)             │
│  │ Layer 2     │ Minimum Free Energy (MFE)                      │
│  │ Layer 3     │ Strand Asymmetry                               │
│  │ Layer 4     │ 15-mer Homology Exclusion                      │
│  │ Layer 5     │ Full 21-nt Identity Screen                    │
│  │ Layer 6     │ Seed Region Matching (positions 2-8)          │
│  │ Layer 7     │ Palindrome Detection                          │
│  │ Layer 8     │ CpG Immunogenicity                           │
│  │ Layer 9     │ Poly-runs & Entropy                           │
│  └────────────┘                                                │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                             │
│  │  SAFETY SCORE   │ → 0-100 (100 = perfect safety)            │
│  └─────────────────┘                                             │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                             │
│  │  EFFICACY SCORE │ → 0-100 (based on Reynolds rules)         │
│  └─────────────────┘                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Layer-by-Layer Analysis

### Layer 1: GC Content (Thermodynamic Stability)

**Theory:** G-C pairs have 3 hydrogen bonds (strong), A-T pairs have 2 (weak).
- Too many G-C (>52%): Strand too rigid to unwind
- Too few G-C (<30%): Strand too fragile to survive

**Implementation:**
```python
def calculate_gc_content(seq: str) -> float:
    if not seq: return 0.0
    gc = sum(1 for c in seq if c in 'GC')
    return (gc / len(seq)) * 100
```

**Safety Penalty:**
| GC Content | Penalty |
|------------|---------|
| 30-52% | 0 (No penalty) |
| 36-52% (optimal) | +8.0 efficacy bonus |
| 25-30% or 52-60% | -5.0 penalty |
| <25% or >60% | -12.0 penalty |

---

### Layer 2: Minimum Free Energy (MFE)

**Theory:** MFE tells how thermodynamically stable the siRNA duplex is. More negative = more stable.

**Implementation:**
```python
def calculate_mfe(seq: str) -> float:
    seq = seq.upper().replace('U', 'T')
    total_dh, total_ds = 0.0, 0.0
    
    for i in range(len(seq) - 1):
        dinuc = seq[i:i+2]
        if dinuc in NN_PARAMS:
            dh, ds = NN_PARAMS[dinuc]
            total_dh += dh
            total_ds += ds
    
    # ΔG = ΔH - T·ΔS at 37°C
    mfe = total_dh - 310.15 * (total_ds / 1000.0)
    return round(mfe, 2)
```

**Output:** MFE value in kcal/mol (typically -20 to -35 for good siRNA)

---

### Layer 3: Strand Asymmetry (Duplex-End Stability)

**Theory:** For proper RISC loading, the 5' end should be thermodynamically weaker than the 3' end.

**Implementation:**
```python
def calculate_asymmetry(seq: str) -> float:
    seq = seq.upper().replace('U', 'T')
    
    def end_energy(s):
        e = 0.0
        for i in range(len(s) - 1):
            d = s[i:i+2]
            if d in NN_PARAMS:
                dh, ds = NN_PARAMS[d]
                e += dh - 310.15 * (ds / 1000.0)
        return e
    
    # Positive = 5' end weaker = GOOD
    return round(end_energy(seq[-4:]) - end_energy(seq[:4]), 2)
```

**Output:**
- Positive value: Favorable (guide strand selection works)
- Negative value: Unfavorable (wrong strand may be loaded)

---

### Layer 4: 15-mer Homology Exclusion (Off-Target Safety)

**Theory:** If ≥15 contiguous nucleotides match a non-target genome, it's lethal toxicity.

**Implementation:**
```python
def find_max_homology(seq: str, non_target: str, bloom_index=None) -> int:
    # Strategy 1: Bloom Filter (O(1) fast)
    if bloom_index and bloom_index.is_built:
        result = bloom_index.check_homology(seq)
        return result["maxMatchLength"]
    
    # Strategy 2: Exact substring search (O(n²))
    if not non_target:
        return 0
    for l in range(len(seq), 3, -1):
        for i in range(len(seq) - l + 1):
            if seq[i:i+l] in non_target:
                return l
    return 0
```

**Safety Penalty:**
```python
if match_len >= 15:
    safety_score -= (match_len - 14) * 15.0
```

| Match Length | Safety Penalty |
|--------------|----------------|
| 15 bp | -15 points |
| 16 bp | -30 points |
| 17 bp | -45 points |
| 21 bp (full) | -100 points |

---

### Layer 5: Full 21-nt Identity Screen

**Theory:** Even stricter - checks if the *entire* 21-letter sequence appears verbatim in the non-target genome.

**Implementation:**
```python
def check_full_21nt_identity(seq: str, non_target: str) -> bool:
    if not non_target or len(seq) < 21:
        return False
    return seq[:21] in non_target
```

**Safety Penalty:** -100 points (immediate rejection)

---

### Layer 6: Seed Region Matching (Positions 2-8)

**Theory:** The "Seed Region" (letters 2 through 8) is the targeting radar. If this matches non-target genes, catastrophic off-target silencing occurs.

**Implementation:**
```python
seed_seq = seq[1:8]  # Positions 2-8 (0-indexed)
if non_target_sequence:
    seed_match_count = non_target_sequence.count(seed_seq)
    has_seed_match = seed_match_count > 0
```

**Safety Penalty:**
```python
if has_seed_match: safety_score -= min(seed_match_count * 5.0, 30.0)
```

---

### Layer 7: Palindrome Detection (Hairpin Risk)

**Theory:** A palindromic sequence reads identically in reverse-complement. This causes the RNA to fold onto itself, destroying its function.

**Implementation:**
```python
def check_palindrome(seq: str) -> (bool, int):
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    for length in range(8, 5, -1):
        for i in range(len(seq) - length + 1):
            sub = seq[i:i+length]
            rev_comp = "".join(complement.get(c, c) for c in reversed(sub))
            if sub == rev_comp:
                return True, length
    return False, 0
```

**Safety Penalty:**
```python
if is_palin: safety_score -= (palin_len * 4.0)
```

---

### Layer 8: CpG Immunogenicity

**Theory:** "CG" dinucleotides trigger Toll-Like Receptor 9 (TLR9) in humans, causing autoimmune inflammatory response.

**Implementation:**
```python
def has_cpg_motif(seq: str) -> bool:
    return "CG" in seq

IMMUNE_MOTIFS = ["CG", "TGTGT", "GTCCTTCAA", "GACTATGTGGAT"]
```

**Safety Penalty:**
```python
if cpg: safety_score -= 20.0
if len(immune_hits) > 0: safety_score -= (len(immune_hits) * 15.0)
```

---

### Layer 9: Poly-runs, AT-Repeats & Entropy

**Theory:**
- **Poly-runs** (AAAA): Cause polymerase slippage during manufacturing
- **AT-repeats** (ATATAT): Cause transcription termination errors
- **Low Shannon Entropy**: Sequence is repetitive and unreliable

**Implementation:**
```python
def has_poly_run(seq: str) -> bool:
    for base in "ATCG":
        if base * 4 in seq: return True
    return False

def has_at_dinuc_repeat(seq: str) -> bool:
    return "ATATAT" in seq or "TATATA" in seq

def calculate_shannon_entropy(seq: str) -> float:
    if not seq: return 0.0
    freq = {}
    for c in seq:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0.0
    for count in freq.values():
        p = count / len(seq)
        if p > 0: entropy -= p * math.log2(p)
    return round(entropy, 3)
```

**Safety Penalties:**
| Issue | Penalty |
|-------|---------|
| Poly-run | -25 points |
| AT-repeat | -15 points |
| Entropy < 1.7 | -(1.7 - entropy) × 40 |

---

## Complete Safety Scoring Formula

```python
safety_score = 100.0

# Layer 1: 15-mer Exclusion
if match_len >= 15: safety_score -= (match_len - 14) * 15.0

# Layer 2: Full 21-nt Identity
if full_21nt: safety_score -= 100.0

# Layer 3: Seed Region Match
if has_seed_match: safety_score -= min(seed_match_count * 5.0, 30.0)

# Layer 4: Palindrome
if is_palin: safety_score -= (palin_len * 4.0)

# Layer 5: CpG
if cpg: safety_score -= 20.0

# Layer 6: Poly-run
if poly: safety_score -= 25.0

# Layer 7: Extended Immune Motifs
if len(immune_hits) > 0: safety_score -= (len(immune_hits) * 15.0)

# Layer 8: Entropy
if entropy < 1.7: safety_score -= ((1.7 - entropy) * 40.0)

# Layer 9: AT-repeats
if at_repeat: safety_score -= 15.0

# Continuous GC Penalty
gc_deviation = abs(gc - 41.0)
if gc_deviation > 15: safety_score -= 15.0
elif gc_deviation > 10: safety_score -= 8.0
elif gc_deviation > 5: safety_score -= 3.0

safety_score = max(0.0, min(100.0, safety_score))
```

---

## Efficacy Scoring (Reynolds Rules)

### Theory

Based on Reynolds et al. (2004), specific nucleotides at specific positions correlate with silencing efficiency.

### Position-Specific Preferences

| Position | Preferred | Avoid |
|----------|-----------|-------|
| 1 (5' end) | A, T | G, C |
| 3 | A | G, C |
| 10 (Ago2 cleavage) | A | G |
| 19 (3' end) | A, T | G, C |
| 21 (3' terminal) | G, C | A, T |

### Implementation

```python
def calculate_efficacy(seq: str, gc: float) -> float:
    score = 40.0  # Base score
    
    # Position-specific bonuses
    position_prefs = {
        0: {'A': 3.5, 'T': 3.5, 'G': -2.0, 'C': -2.0},
        2: {'A': 3.0, 'T': 0.0, 'G': -1.5, 'C': 0.0},
        9: {'A': 4.0, 'T': 1.0, 'G': -2.0, 'C': -1.0},
        18: {'A': 3.5, 'T': 3.0, 'G': -2.0, 'C': -2.0},
        # ... all 20 positions
    }
    
    for i in range(min(length, 20)):
        nt = seq[i]
        if i in position_prefs:
            score += position_prefs[i].get(nt, 0)
    
    # GC content bonus
    if 36 <= gc <= 52: score += 8.0
    elif 30 <= gc <= 55: score += 3.0
    
    # Dinucleotide penalties
    if seq[-2:] == 'AA': score -= 4.0
    if 'AAAA' in seq: score -= 5.0
    
    # Internal stability
    at_5p = sum(1 for c in seq[:5] if c in 'AT')
    at_3p = sum(1 for c in seq[-5:] if c in 'AT')
    score += (at_5p - at_3p) * 2.0
    
    return max(0.0, min(100.0, round(score, 1)))
```

---

# 5. V7 Model: Deep Learning Foundation (RiNALMo-v2)

## Overview

RiNALMo-v2 is a **hybrid neural network** that combines:
1. **Transformer architecture** (for learning sequence patterns)
2. **Physics-informed features** (for incorporating thermodynamic rules)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RiNALMo-v2 ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: 21-nt siRNA sequence                                     │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ K-mer Embedding Layer (k=4, vocab=256)                   │    │
│  │ Maps 4-mers to 64-dimensional vectors                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Positional Encoding (Sinusoidal)                         │    │
│  │ Adds sequence position awareness                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Transformer Block 1 (4 attention heads)                  │    │
│  │ Self-attention: captures long-range interactions       │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Transformer Block 2                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Transformer Block 3                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Global Average Pooling                                    │    │
│  │ Aggregates sequence representation                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Efficacy Prediction Head                                  │    │
│  │ FFN(64) → GELU → FFN(32) → GELU → FFN(1) → Sigmoid   │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Hybrid Ensemble (60% DL + 40% Physics)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│           │                                                     │
│           ▼                                                     │
│  Output: Efficacy Score (0-100)                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Model Parameters

| Component | Value |
|-----------|-------|
| K-mer Size | 4 |
| Vocabulary | 256 (4⁴) |
| Embedding Dimension | 64 |
| Attention Heads | 4 |
| Transformer Layers | 3 |
| Feed-Forward Dimension | 256 |
| Dropout | 0.1 |
| **Total Parameters** | ~191,000 |

## Key Components

### 1. K-mer Embedding

Instead of embedding single nucleotides (vocab=4), we embed all possible 4-mers (vocab=256):

```python
class KMerEmbedding(nn.Module):
    def __init__(self, k: int = 4, embed_dim: int = 64):
        self.vocab_size = 4 ** k  # 256 for k=4
        self.embedding = nn.Embedding(self.vocab_size + 1, embed_dim)
    
    def kmer_to_idx(self, kmer: str) -> int:
        """Convert k-mer string to integer index."""
        val = 0
        for c in kmer:
            val = val * 4 + {'A': 0, 'C': 1, 'G': 2, 'T': 3}[c]
        return val + 1
    
    def forward(self, seq: str) -> torch.Tensor:
        """Extract k-mers and return embeddings."""
        indices = [self.kmer_to_idx(seq[i:i+self.k]) 
                   for i in range(len(seq) - self.k + 1)]
        return self.embedding(torch.tensor(indices))
```

**Why K-mers?**
- Captures local sequence motifs (CpG islands, poly-A signals)
- More biologically meaningful than single nucleotides
- Used in DNABERT-2, other genomic foundation models

### 2. Positional Encoding

Allows the transformer to understand where each k-mer is in the sequence:

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int = 64, max_len: int = 128):
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]
```

### 3. Multi-Head Self-Attention

Allows attending to different parts of the sequence simultaneously:

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, embed_dim: int = 64, num_heads: int = 4):
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.qkv_proj = nn.Linear(embed_dim, 3 * embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        
        qkv = self.qkv_proj(x).reshape(batch_size, seq_len, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn_weights = F.softmax(attn_scores, dim=-1)
        
        output = torch.matmul(attn_weights, v)
        output = output.transpose(1, 2).reshape(batch_size, seq_len, -1)
        
        return self.out_proj(output)
```

### 4. Physics-Informed Features

We inject domain knowledge (thermodynamic rules) into the model:

```python
class PhysicsInformedFeatures:
    def extract(self, seq: str) -> dict:
        gc = (seq.count('G') + seq.count('C')) / len(seq) * 100
        
        # GC window scoring
        gc_window_score = 10.0 if 35 <= gc <= 55 else (-8.0 if gc < 30 or gc > 60 else 3.0)
        
        # Position-specific scoring
        position_score = sum(self.position_prefs[i].get(seq[i], 0) 
                            for i in range(min(len(seq), 20)))
        
        # Dinucleotide penalties
        dinuc_penalty = 0.0
        if seq.endswith('AA'): dinuc_penalty -= 4.0
        if 'GGGG' in seq or 'CCCC' in seq: dinuc_penalty -= 10.0
        
        return {
            'gc_content': gc,
            'gc_window_score': gc_window_score,
            'position_score': position_score,
            'dinuc_penalty': dinuc_penalty,
            # ... more features
        }
```

### 5. Hybrid Ensemble

Combines DL predictions with physics-based predictions:

```python
def predict(self, seq: str) -> dict:
    # Deep learning prediction
    dl_efficacy = self.transformer(seq).item()
    
    # Physics-based prediction
    features = self.physics.extract(seq)
    physics_efficacy = self._physics_predict(features)
    
    # Weighted ensemble (60% DL + 40% Physics)
    combined = 0.6 * dl_efficacy + 0.4 * physics_efficacy
    
    return {
        'dl_efficacy': round(dl_efficacy * 100, 1),
        'physics_efficacy': round(physics_efficacy * 100, 1),
        'combined_efficacy': round(combined * 100, 1),
    }
```

---

# 6. V8 Advanced Features

## 6.1 Resistance Evolution Model (Cocktail Design)

### Problem

A single siRNA can be evaded by a single point mutation in the target. This leads to resistance.

### Solution

Design a **cocktail of 3 non-overlapping siRNAs** targeting different regions of the same gene. The pest would need 3 simultaneous mutations to develop resistance.

### Algorithm

```python
def design_cocktail(sequence, si_length=21, num_targets=3):
    """
    Select non-overlapping siRNA candidates for cocktail design.
    """
    # Generate all candidates
    all_candidates = run_first_model_pipeline(sequence, ...)
    
    # Select top non-overlapping candidates
    cocktail = []
    used_ranges = []
    
    for cand in all_candidates:
        # Skip unsafe candidates
        if cand["safetyScore"] < 70:
            continue
        
        pos = cand["position"]
        
        # Check for overlap
        overlaps = False
        for (start, end) in used_ranges:
            if not (pos + si_length <= start or pos >= end):
                overlaps = True
                break
        
        if not overlaps:
            cocktail.append(cand)
            used_ranges.append((pos, pos + si_length))
        
        if len(cocktail) >= num_targets:
            break
    
    # Calculate synergy score
    avg_safety = sum(c["safetyScore"] for c in cocktail) / len(cocktail)
    avg_efficacy = sum(c["efficiency"] for c in cocktail) / len(cocktail)
    coverage = len(cocktail) / num_targets * 100
    
    synergy = (avg_safety * 0.4 + avg_efficacy * 0.4 + coverage * 0.2)
    
    return {
        "cocktail": cocktail,
        "synergyScore": synergy,
        # ...
    }
```

### Cocktail Synergy Formula

```
Synergy = (Avg_Safety × 0.4) + (Avg_Efficacy × 0.4) + (Coverage × 0.2)
```

---

## 6.2 AI Chemical Modification Optimizer with SVG Visualization

### Problem

Chemical modifications (2'-OMe, 2'-F, PS) can stabilize siRNA, but modifying the wrong positions reduces efficacy. Users need to visualize where modifications occur.

### Solution

Monte-Carlo AI that tests 2000+ modification layouts AND generates interactive 2D SVG visualizations showing:
- Native (unmodified) RNA structure
- Modified RNA with color-coded modification markers
- Side-by-side comparison view
- Linear sequence view with modification positions

### Modification Types

| Type | Stability Boost | Ago2 Penalty | Best For |
|------|----------------|-------------|----------|
| 2'-OMe | +2.5h/nt | -1.8%/nt | General use |
| 2'-F | +3.0h/nt | -0.8%/nt | High stability needed |
| PS | +4.0h/nt | -2.5%/nt | Maximum nuclease resistance |

### Critical Rule: Ago2 Cleavage Zone

**Positions 9-12 must NEVER be modified!** These are where RISC cuts the target mRNA.

```
Position: 1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21
          │  │  │  │  │  │  │  │  │  │   │  │  │  │  │  │  │  │  │  │  │
          ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼   ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼
         [✓][✓][✓][✓][✓][✓][✓][✓][✗][✗][✗][✗][✓][✓][✓][✓][✓][✓][✓][✓][✓]
                              ↑
                      DO NOT MODIFY!
```

### Monte-Carlo Algorithm with SVG Generation

```python
def ai_optimize_modifications(sequence, iterations=2000, generate_svg=True):
    """
    AI-driven chemical modification optimizer.
    Tests random modification layouts to find the best Therapeutic Index.
    Automatically generates SVG visualizations for comparison.
    """
    best_result = None
    best_score = -1.0
    
    for _ in range(iterations):
        # Random modification type
        mod_type = random.choice(["2_ome", "2_f", "ps"])
        
        # Random positions (avoiding cleavage zone)
        num_mods = random.randint(5, 14)
        positions = random.sample(available_positions, num_mods)
        
        # Skip over-modified (>65%)
        if num_mods / len(sequence) > 0.65:
            continue
        
        # Score this layout
        result = apply_modifications(sequence, mod_type, positions)
        
        if result["therapeuticIndex"] > best_score:
            best_score = result["therapeuticIndex"]
            best_result = result
    
    # Generate SVG visualizations
    if generate_svg:
        from svg_generator import RNASVGenerator
        svg_gen = RNASVGenerator()
        best_result["svgFiles"] = {
            "native": svg_gen.generate_native_svg(sequence),
            "modified": svg_gen.generate_modified_svg(sequence, best_modifications),
            "comparison": svg_gen.generate_comparison_svg(sequence, best_modifications),
            "linear": svg_gen.generate_linear_view_svg(sequence, best_modifications),
        }
    
    return best_result
```

### SVG Visualization Output

```
┌─────────────────────────────────────────────────────────────────────┐
│  RNA Chemical Modification Comparison                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  NATIVE (Unmodified)     │    MODIFIED                              │
│  ┌─────────────────┐     │    ┌─────────────────┐                   │
│  │  A U G G A C U  │     │    │  A U G G A C U  │                   │
│  │  │ │ │ │ │ │ │  │     │    │  │ │ │ │ │ │ │  │                   │
│  │  (A)(U)(G)(G)...│     │    │  [A][U][G][G]...│                   │
│  │   No markers    │     │    │   ● ● ●    ● ●  │                   │
│  └─────────────────┘     │    │  (2'-OMe markers)│                   │
│                          │    └─────────────────┘                   │
│                                                                      │
│  Modification: 2'-OMe(4), 2'-F(1), PS(2)                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Therapeutic Index Formula

```
Therapeutic_Index = (Half_Life / 72 × 50) + (Ago2_Affinity / 100 × 50)

Higher = Better balance of stability vs. efficacy
```

---

## 6.3 RNA Target Accessibility

### Problem

Even a perfectly designed siRNA fails if the target site on the mRNA is buried in secondary structures.

### Solution

Calculate the thermodynamic accessibility of the target site.

### Theory

```
For RISC to bind:
1. siRNA must bind to target (ΔG_binding)
2. Target site must be accessible (ΔG_unfolding)

Net Energy = ΔG_binding - ΔG_unfolding

If Net < -10 kcal/mol: Site is accessible
If Net > 0 kcal/mol: Site is blocked
```

### Implementation

```python
def calculate_accessibility(sequence, target_context=None):
    """
    Calculate thermodynamic accessibility score.
    """
    # Calculate binding energy
    dg_binding = _calc_duplex_dg(sequence, complement)
    
    # Estimate unfolding cost
    dg_unfolding = _estimate_target_folding_dg(target_context)
    
    # Net energy
    dg_net = dg_binding - dg_unfolding
    
    # Convert to 0-100 score
    if dg_net < -20: acc_score = 100.0
    elif dg_net < -15: acc_score = 90.0 + ((-15 - dg_net) / 5.0) * 10.0
    elif dg_net < -10: acc_score = 70.0 + ((-10 - dg_net) / 5.0) * 20.0
    # ... more brackets
    
    return {
        "accessibilityScore": acc_score,
        "accessibilityClass": classify(acc_score),
        "dgNet": dg_net,
    }
```

### Accessibility Classification

| Score | Class | Interpretation |
|-------|-------|----------------|
| 80-100 | Open | Highly accessible |
| 55-79 | Moderate | Should bind normally |
| 30-54 | Restricted | May have reduced efficacy |
| 0-29 | Blocked | RISC cannot enter |

---

## 6.4 RNA Secondary Structure Prediction (NEW!)

### Problem

Users want to **VISUALIZE** the actual 2D folding of the RNA, not just get a score. They want to see hairpins, loops, stems, and bulges.

### Solution

Use **ViennaRNA (RNAfold algorithm)** for accurate MFE structure prediction, with Nussinov as fallback.

### Theory

```
ViennaRNA Package - Same as RNAfold Web Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The RNAfold algorithm from ViennaRNA Suite uses:

1. Dynamic Programming for MFE calculation
2. Turner energy parameters (1999/2004)
3. Nearest-neighbor thermodynamic model
4. Partition function for ensemble analysis

This is the SAME algorithm used by:
- RNAfold web server (rna.tbi.univie.ac.at)
- UNAFold
- Many other RNA structure prediction tools
```

```
RNA molecules fold into specific secondary structures based on Watson-Crick
and Wobble base pairing:

Base Pairing Rules:
┌─────────────────────────────────────────────────────────────┐
│  A ───── U    (2 hydrogen bonds)                            │
│  G ───── C    (3 hydrogen bonds)  ← Strongest              │
│  G ───── U    (Wobble pair - 2 bonds, less stable)       │
└─────────────────────────────────────────────────────────────┘

Structure Elements:
┌─────────────────────────────────────────────────────────────┐
│  Hairpin Loop:     Nucleotides forming a loop              │
│  Stem:            Stacked base pairs                       │
│  Internal Loop:   Gap in pairing on both strands          │
│  Bulge:           Gap in pairing on one strand             │
│  Multi-loop:      Junction of 3+ stems                   │
└─────────────────────────────────────────────────────────────┘
```

### Nussinov Algorithm

The algorithm finds optimal folding by **dynamic programming**, maximizing base pairs:

```python
class NussinovSolver:
    """
    Nussinov Algorithm for RNA Secondary Structure Prediction.
    
    Key features:
    - Maximizes number of base pairs
    - No pseudoknots (no crossing structures)
    - Minimum hairpin loop size: 3 nucleotides
    - Only canonical base pairs (GC, AU, GU)
    """
    
    def predict(self, sequence: str) -> dict:
        """
        Predict secondary structure.
        
        Returns:
        - dot_bracket: Structure notation (e.g., "((..))")
        - base_pairs: List of predicted pairs
        - elements: Structural elements (hairpins, stems, etc.)
        - accessibility_prediction: Accessibility analysis
        - visual: ASCII visualization
        """
        # Step 1: Initialize DP table
        self.dp = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Step 2: Fill DP table using recurrence:
        # DP[i][j] = max of:
        #   - DP[i][j-1] (j unpaired)
        #   - DP[i][k-1] + DP[k+1][j-1] + 1 (pair k with j)
        
        # Step 3: Traceback to find base pairs
        # Step 4: Generate dot-bracket notation
        # Step 5: Identify structural elements
```

### Base Pair Energy Parameters

| Pair | Energy (kcal/mol) | Description |
|------|-------------------|-------------|
| GC | -3.0 | Strongest (3 H-bonds) |
| CG | -3.0 | Strongest (3 H-bonds) |
| AU | -2.0 | Moderate (2 H-bonds) |
| UA | -2.0 | Moderate (2 H-bonds) |
| GU | -1.0 | Wobble (2 H-bonds, less stable) |
| UG | -1.0 | Wobble (2 H-bonds, less stable) |

### Example Output

```
Input Sequence: AUGGACUACAAGGACGACGA

┌─────────────────────────────────────────────────────────────────────┐
│ PREDICTED 2D STRUCTURE                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  5'-A-U-G-G-A-C-U-A-C-A-A-G-G-A-C-G-A-C-G-A-3'                   │
│         |   | |   | |   |   |   |   |                            │
│        (A-U) (G-C) (U-A) (A-U) (G-C)                              │
│                                                                      │
│  Dot-Bracket: .(((.((...))..)..)).                                 │
│                                                                      │
│  Structure Elements:                                                 │
│  • Stem helix (2 base pairs) positions 1-3                        │
│  • Hairpin loop (3 nt) positions 4-6                              │
│  • Stem helix (2 base pairs) positions 7-9                        │
│  • 5' overhang (1 nt)                                             │
│  • 3' overhang (1 nt)                                             │
│                                                                      │
│  Accessibility: 75% (Moderately Accessible)                          │
│  Structure Score: 60/100                                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Dot-Bracket Notation

| Symbol | Meaning |
|--------|---------|
| `.` | Unpaired nucleotide |
| `(` | Opening bracket (pairs with closing) |
| `)` | Closing bracket (pairs with opening) |

### API Endpoint

```python
@app.route("/api/rna_structure", methods=["POST"])
def rna_structure():
    """
    Predict RNA secondary structure using Nussinov algorithm.
    
    Returns:
    - sequence: Cleaned RNA sequence
    - dot_bracket: Structure notation
    - structure_score: Stability score (0-100)
    - num_base_pairs: Number of predicted pairs
    - base_pairs: List of base pairs with positions
    - elements: Structural elements
    - accessibility_prediction: Accessibility analysis
    - visual: ASCII visualization
    """
```

---

## 6.5 PDB Structure Visualization (NEW!)

### Problem

Users need to **visualize** the 3D structure of siRNA molecules to understand how chemical modifications affect the structure. They need to see the difference between native and modified RNA.

### Solution

Generate **PDB (Protein Data Bank)** files for RNA structures that can be viewed in molecular visualization tools like PyMOL, VMD, or Chimera.

### Theory

```
PDB Format Structure:
┌─────────────────────────────────────────────────────────────┐
│  ATOM   1  P    A    A    1      9.234  10.123  15.678     │
│  ATOM   2  OP1  A    A    1      8.123  11.234  15.900     │
│  ATOM   3  C1'  RIB  A    1      6.234  10.456  15.123     │
│  ...                                                         │
│  ATOM  --  CME  MTL  A    1      7.234  11.123  14.678     │ ← 2'-OMe
│  ATOM  --  F2P  RIB  A    1      7.456  11.456  14.890     │ ← 2'-F
└─────────────────────────────────────────────────────────────┘

Atom Types:
- P: Phosphate backbone
- C1', C2', C3', C4': Sugar carbons
- O2': 2'-OH oxygen
- CME: 2'-O-Methyl carbon
- F2P: 2'-Fluoro phosphor
- S: Sulfur (in PS backbone)
```

### A-Form RNA Geometry

Standard A-form RNA double helix parameters:

| Parameter | Value |
|-----------|-------|
| Helical Radius | 9.0 Å |
| Base Pair Rise | 2.56 Å |
| Base Pair Twist | 32.7° |
| Major Groove | 12.0 Å |
| Minor Groove | 6.0 Å |

### Chemical Modification Representation

| Modification | PDB Atom | Color (PyMOL) | Description |
|--------------|----------|---------------|-------------|
| Native | O2' | Green | Standard 2'-OH group |
| 2'-OMe | CME, C1', C2', C3' | Blue | Methyl group added to O2' |
| 2'-F | F2P | Orange | Fluorine replaces O2' |
| PS | S | Purple | Sulfur replaces non-bridging O |

### Implementation

```python
class RNAPDBGenerator:
    """
    Generates PDB files for A-form RNA double helices.
    Supports chemical modifications for visualization.
    """
    
    def generate_native_pdb(self, sequence: str) -> str:
        """Generate canonical A-form RNA helix."""
        pdb_lines = []
        for i, base in enumerate(sequence):
            angle = math.radians(i * 32.7)
            rise = i * 2.56
            helix_x = 9.0 * math.cos(angle)
            helix_y = 9.0 * math.sin(angle)
            
            # Generate P, sugar, base atoms
            pdb_lines.extend(self._get_phosphate_atoms(...))
            pdb_lines.extend(self._get_sugar_atoms(...))
            pdb_lines.extend(self._get_base_atoms(...))
        
        return "\n".join(pdb_lines)
    
    def generate_modified_pdb(self, sequence: str, 
                            modifications: Dict[int, str]) -> str:
        """Generate modified RNA with specified chemical changes."""
        # Add modification atoms (CME, F2P, S)
        ...
```

### Visualization in PyMOL

```bash
# Load structures
load native.pdb, native
load modified.pdb, modified

# Show as cartoon
show cartoon

# Color modifications
color blue, resn MTL  # 2'-OMe
color orange, resn F2P  # 2'-F
color purple, resn PSU  # Phosphorothioate

# Export image
ray 1200, 800
png structure_comparison.png, dpi=300
```

### Output Files

| File | Description | Use Case |
|------|------------|----------|
| `*_native.pdb` | Unmodified RNA | Baseline comparison |
| `*_modified.pdb` | Modified RNA | Show chemical changes |
| `*_comparison.pdb` | Both models | Side-by-side comparison |
| `*.pml` | PyMOL script | Automated visualization |

---

## 6.6 Tissue-Specific Off-Target Filtering

### Problem

Standard homology checks flag genes as "risky" regardless of where the siRNA is delivered.

### Solution

Check if off-target genes are expressed in the **delivery tissue**.

### Theory

```
If an off-target gene is only expressed in the heart,
but we deliver siRNA to the liver,
the off-target risk is effectively ZERO.
```

### Implementation

```python
def check_tissue_off_target(gene, organism, delivery_tissue):
    """
    Check if off-target gene is expressed in delivery tissue.
    """
    db = load_tissue_database()
    tissues = db[organism]["tissues"]
    
    delivery_genes = tissues[delivery_tissue]["expressed_genes"]
    
    is_expressed = gene.upper() in [g.upper() for g in delivery_genes]
    
    if is_expressed:
        threat = "High"
    else:
        other_tissues = [t for t in tissues if gene in tissues[t]["expressed_genes"]]
        threat = "Low" if other_tissues else "None"
    
    return {
        "isExpressedInDeliveryTissue": is_expressed,
        "effectiveThreatLevel": threat,
    }
```

---

# 7. API Reference

## 7.1 Flask Endpoints (Port 5000)

### Main Pipeline

#### `POST /api/first_model`
Run the complete V6 9-layer safety pipeline.

**Request:**
```json
{
  "sequence": "ATGCGTACGATCGATCG...",
  "siLength": 21,
  "nonTargetSequence": "GATTACA...",
  "geneName": "actin"
}
```

**Response:**
```json
{
  "candidates": [
    {
      "position": 1,
      "sequence": "ATGCGTACGATCGATCGATCG",
      "gcContent": 47.6,
      "safetyScore": 95.0,
      "efficiency": 85.2,
      "mfe": -28.45,
      "asymmetry": 1.23,
      "endStability": "favorable",
      "matchLength": 0,
      "hasCpGMotif": false,
      "hasPolyRun": false,
      "hasPalindrome": false,
      "essentialityScore": 92.5,
      "compositeScore": 91.5,
      "status": "CLEARED"
    }
  ]
}
```

---

### Cocktail Design

#### `POST /api/cocktail`
Design multi-target siRNA cocktail.

**Request:**
```json
{
  "sequence": "ATGCGTACGATCG...",
  "siLength": 21,
  "nonTargetSequence": "",
  "numTargets": 3
}
```

**Response:**
```json
{
  "cocktail": [...],
  "numSelected": 3,
  "avgSafety": 95.3,
  "avgEfficacy": 87.2,
  "coveragePercent": 100.0,
  "synergyScore": 93.5
}
```

---

### Chemical Modification

#### `POST /api/chem_ai`
AI-optimized chemical modification.

**Request:**
```json
{
  "sequence": "ATGGACTACAAGGACGACGA"
}
```

**Response:**
```json
{
  "modifiedSequence": "[A*][T*][G*][G*]A[C*]...",
  "modificationType": "2'-Fluoro (2'-F)",
  "stabilityHalfLife": 36.6,
  "ago2Affinity": 85.6,
  "therapeuticIndex": 68.2,
  "searchStats": {
    "totalIterations": 2000,
    "layoutsEvaluated": 1773
  }
}
```

---

### PDB Structure Visualization (NEW!)

#### `POST /api/pdb/generate`
Generate PDB files for RNA structure visualization.

**Request:**
```json
{
  "sequence": "AUGGACUACAAGGACGACGA",
  "modifications": {
    "0": "2_ome",
    "2": "2_ome",
    "4": "2_f",
    "17": "ps",
    "18": "ps"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "native_pdb": "/path/to/native.pdb",
  "modified_pdb": "/path/to/modified.pdb",
  "comparison_pdb": "/path/to/comparison.pdb",
  "pdb_content": "ATOM  ...",
  "sequence": "AUGGACUACAAGGACGACGA",
  "modifications": {"0": "2_ome", ...}
}
```

#### `POST /api/pdb/native`
Generate only the native (unmodified) RNA PDB.

#### `POST /api/pdb/modified`
Generate PDB with specified chemical modifications.

---

### RNA Accessibility

#### `POST /api/rna_accessibility`
Calculate RNA target accessibility.

**Request:**
```json
{
  "sequence": "ATGGACTACAAGGACGACGA",
  "targetContext": "AUGCUGCUAUGCUG..."
}
```

**Response:**
```json
{
  "dgBinding": -32.5,
  "dgUnfolding": 8.7,
  "dgNet": -23.8,
  "accessibilityScore": 95.0,
  "accessibilityClass": "Open"
}
```

---

### RNA Secondary Structure (NEW!)

#### `POST /api/rna_structure`
Predict RNA secondary structure using Nussinov algorithm.

**Request:**
```json
{
  "sequence": "ATGGACTACAAGGACGACGA"
}
```

**Response:**
```json
{
  "sequence": "AUGGACUACAAGGACGACGA",
  "length": 20,
  "dot_bracket": ".(((.((...))..)..)).",
  "structure_score": 60.0,
  "num_base_pairs": 5,
  "base_pairs": [
    [1, 2, 19, "UG", -1.0],
    [2, 3, 18, "GC", -3.0],
    [3, 4, 15, "GC", -3.0],
    [5, 6, 12, "CG", -3.0],
    [6, 7, 11, "UA", -2.0]
  ],
  "elements": [
    {
      "type": "stem",
      "description": "Stem helix (2 base pairs)"
    },
    {
      "type": "hairpin_loop",
      "description": "Hairpin loop (1 nt)"
    }
  ],
  "accessibility_prediction": {
    "classification": "Moderately Accessible",
    "score": 75.0,
    "reason": "Some structure present but should not significantly impede binding"
  },
  "visual": "5'-AUGGACUACAAGGACGACGA-3'\n        ||| ||   ||  |  \n3'-AGCAGCAGGAACAUCAGGUA-5'"
}
```

#### `POST /api/rna_structure/compare`
Compare RNA structure across multiple target sites.

**Request:**
```json
{
  "sequences": ["ATGGACTACAAGGACGACGA", "GCGCGCGCGCGCGCGCGCGC"],
  "positions": [1, 50]
}
```

---

### Tissue Filter

#### `POST /api/tissue_filter`
Filter off-targets by tissue expression.

**Request:**
```json
{
  "sequence": "ATGGACTACAAGGACGACGA",
  "offTargetGenes": ["CYP3A4", "MBP"],
  "organism": "homo_sapiens",
  "deliveryTissue": "liver"
}
```

**Response:**
```json
{
  "totalOffTargets": 2,
  "genuineThreats": 1,
  "clearedAsSafe": 1,
  "adjustedSafetyRating": "CAUTION",
  "details": [...]
}
```

---

## 7.2 FastAPI Endpoints (Port 8000)

### Health Check

#### `GET /health`
Check if RiNALMo-v2 is running.

**Response:**
```json
{
  "status": "healthy",
  "model": "RiNALMo-v2",
  "torch_available": true,
  "features": ["mfe", "asymmetry", "transformer", "physics_hybrid"]
}
```

---

### Batch Prediction

#### `POST /predict/efficacy/batch`
Get efficacy predictions from RiNALMo-v2.

**Request:**
```json
{
  "sequences": [
    "ATGGACTACAAGGACGACGA",
    "GCTAGCTAGCTAGCTAGCTA"
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "sequence": "ATGGACTACAAGGACGACGA",
      "efficacy_score": 85.7,
      "dl_efficacy": 88.2,
      "physics_efficacy": 82.1,
      "mfe_score": -28.45,
      "asymmetry_score": 1.23,
      "gc_content": 47.6,
      "end_stability": "favorable",
      "model_info": {
        "name": "RiNALMo-v2",
        "parameters": 191297
      }
    }
  ],
  "model_name": "RiNALMo-v2",
  "model_type": "Hybrid Transformer + Physics"
}
```

---

# 8. Data Flow Diagrams

## 8.1 Complete Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE siRNA DESIGN PIPELINE                         │
└──────────────────────────────────────────────────────────────────────────────┘

USER INPUT
    │
    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. INPUT VALIDATION                                                         │
│    - Parse FASTA / raw sequence                                             │
│    - Validate nucleotides (A, T, C, G)                                      │
│    - Check minimum length (21 bp)                                            │
└──────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. CANDIDATE GENERATION                                                     │
│    - Generate all 21-nt windows                                             │
│    - For each: calculate GC, MFE, asymmetry                                 │
└──────────────────────────────────────────────────────────────────────────────┘
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
┌─────────┐      ┌─────────┐       ┌─────────┐
│ V6      │      │ BLOOM   │       │ ESSEN-  │
│ Safety  │      │ FILTER  │       │ TIALITY │
│ Engine  │      │ Index   │       │ Scoring │
└─────────┘      └─────────┘       └─────────┘
    │                  │                  │
    │                  │                  │
    ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. SAFETY FILTERING (9 Layers)                                              │
│    Layer 1-3: Thermodynamic properties                                       │
│    Layer 4-6: Homology checks                                               │
│    Layer 7-9: Sequence quality                                              │
│                                                                              │
│    OUTPUT: Safety Score (0-100)                                              │
└──────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. EFFICACY SCORING                                                         │
│    - Reynolds rules (position-specific)                                      │
│    - GC content optimization                                                │
│    - Dinucleotide composition                                               │
│                                                                              │
│    OUTPUT: Efficacy Score (0-100)                                             │
└──────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 5. RiNALMo-v2 ENHANCEMENT (Optional)                                         │
│    - K-mer embeddings                                                        │
│    - Transformer attention                                                   │
│    - Physics-informed features                                               │
│    - Hybrid ensemble                                                        │
│                                                                              │
│    OUTPUT: Combined Efficacy (0-100)                                          │
└──────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 6. COMPOSITE SCORING                                                        │
│                                                                              │
│    Composite = (Safety × 0.4) + (Efficacy × 0.3) + (Essentiality × 0.3)      │
│                                                                              │
│    OUTPUT: Composite Score (0-100)                                            │
└──────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 7. RANKING & FILTERING                                                      │
│    - Sort by composite score                                                 │
│    - Filter by minimum thresholds                                            │
│    - Status: CLEARED (>85) or REVIEW (<85)                                  │
└──────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
CANDIDATE RESULTS
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
┌─────────┐      ┌─────────┐       ┌─────────┐
│ VIEW IN │      │ CERTI-  │       │ EXPORT  │
│ TABLE   │      │ FICATE  │       │ CSV     │
└─────────┘      └─────────┘       └─────────┘
```

## 8.2 V8 Advanced Features Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         V8 ADVANCED FEATURES                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐
│  COCKTAIL DESIGN                │
├─────────────────────────────────┤
│                                  │
│  Input: Top N candidates        │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ Non-overlap check         │  │
│  │ (range intersection)      │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ Synergy calculation       │  │
│  │ (weighted average)        │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  Output: 3 siRNAs + synergy    │
│                                  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  AI CHEMICAL OPTIMIZER          │
├─────────────────────────────────┤
│                                  │
│  Input: 21-nt siRNA            │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ Monte-Carlo search       │  │
│  │ (2000 iterations)         │  │
│  └───────────────────────────┘  │
│    │                           │
│    ├───────────────────────────┤
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ Score each layout         │  │
│  │ (Therapeutic Index)       │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  Output: Best modification      │
│  pattern + stats               │
│                                  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  RNA ACCESSIBILITY              │
├─────────────────────────────────┤
│                                  │
│  Input: Target mRNA site        │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ ΔG binding calculation     │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ ΔG unfolding estimation    │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ Net accessibility score   │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  Output: 0-100 + class         │
│                                  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  TISSUE FILTER                  │
├─────────────────────────────────┤
│                                  │
│  Input: Off-target genes       │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ Query tissue database     │  │
│  │ (liver, lung, etc.)      │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  ┌───────────────────────────┐  │
│  │ Check expression in       │  │
│  │ delivery tissue           │  │
│  └───────────────────────────┘  │
│    │                           │
│    ▼                           │
│  Output: Threat levels          │
│  (High/Low/None)               │
│                                  │
└─────────────────────────────────┘
```

---

# 9. Implementation Details

## 9.1 File-by-File Reference

### `web_app/engine.py`

| Function | Lines | Purpose |
|----------|-------|---------|
| `calculate_gc_content()` | 66-71 | GC percentage calculation |
| `calculate_mfe()` | 74-90 | Minimum free energy |
| `calculate_asymmetry()` | 96-115 | Strand asymmetry |
| `calculate_shannon_entropy()` | 119-130 | Sequence complexity |
| `has_cpg_motif()` | 133-134 | CpG detection |
| `has_poly_run()` | 137-142 | Poly-run detection |
| `check_palindrome()` | 159-168 | Hairpin detection |
| `find_max_homology()` | 178-195 | 15-mer homology |
| `calculate_efficacy()` | 207-287 | Reynolds scoring |
| `run_first_model_pipeline()` | 291-441 | Main pipeline |

---

### `web_app/essentiality.py`

| Function | Lines | Purpose |
|----------|-------|---------|
| `calculate_essentiality()` | 61-94 | Main scoring function |
| `_score_single_gene()` | 97-179 | Single gene scoring |
| `get_available_genes()` | 182-186 | List all genes |

**Scoring Formula:**
```
Total = DEG (40) + OGEE (0-30) + RNAi (0-25) + Conservation (5-15)
Max = 100
```

---

### `web_app/bloom_filter.py`

| Class | Lines | Purpose |
|-------|-------|---------|
| `BloomFilter` | 11-98 | Probabilistic set membership |
| `GenomeBloomIndex` | 100-204 | Genome k-mer indexing |

**Memory Efficiency:**
| Genome Size | Raw Storage | Bloom Filter | Compression |
|------------|------------|--------------|-------------|
| 100 MB | 100 MB | ~7 MB | 14× |
| 500 MB | 500 MB | ~35 MB | 14× |
| 3 GB | 3 GB | ~210 MB | 14× |

---

### `backend/main.py`

| Class/Function | Lines | Purpose |
|---------------|-------|---------|
| `KMerEmbedding` | 131-165 | K-mer to vector |
| `PositionalEncoding` | 167-193 | Position awareness |
| `MultiHeadAttention` | 195-231 | Self-attention |
| `TransformerBlock` | 233-250 | Transformer layer |
| `RiNALMoV2` | 252-395 | Full model |
| `PhysicsInformedFeatures` | 397-518 | Domain features |
| `HybridEfficacyPredictor` | 520-615 | Ensemble predictor |

---

## 9.2 Database Schemas

### SQLite: Sequence History

```sql
CREATE TABLE sequence_logs (
    id INTEGER PRIMARY KEY,
    audit_hash VARCHAR(32) UNIQUE,
    sequence VARCHAR(100),
    gc_content FLOAT,
    efficacy FLOAT,
    safety_score FLOAT,
    risk_factors TEXT,
    timestamp DATETIME
);
```

### JSON: Essential Genes

```json
{
  "actin": {
    "essentiality": "essential",
    "organism": "Drosophila melanogaster",
    "evidence": "RNAi screening"
  }
}
```

### JSON: Tissue Expression

```json
{
  "homo_sapiens": {
    "tissues": {
      "liver": {
        "expressed_genes": ["ALB", "CYP3A4", "APOB"],
        "notes": "Primary RNAi delivery target"
      }
    }
  }
}
```

---

# 10. Testing Guide

## 10.1 Manual Testing

### Test 1: Basic Pipeline

1. Open http://localhost:5000
2. Click "RUN DL PIPELINE" with demo data
3. Verify candidates appear in table
4. Check safety scores vary (not all 100%)

### Test 2: RiNALMo-v2 Integration

1. Ensure FastAPI server running on port 8000
2. Select "RiNALMo-v2 Transformer" in dropdown
3. Run pipeline
4. Check for DL efficacy scores in results

### Test 3: Cocktail Design

1. Run pipeline to generate candidates
2. Click "Design Multi-Target Cocktail"
3. Verify 3 non-overlapping siRNAs selected
4. Check synergy score > 85

### Test 4: AI Chemical Optimization

1. Click "AI Chemical Optimization" button
2. Enter sequence: `ATGGACTACAAGGACGACGA`
3. Verify modification pattern appears
4. Check Therapeutic Index > 60

### Test 5: RNA Accessibility

1. Click "RNA Accessibility Check"
2. Enter sequence
3. Verify score and classification

## 10.2 API Testing

```bash
# Health check
curl http://localhost:8000/health

# Batch prediction
curl -X POST http://localhost:5000/api/first_model \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGGACTACAAGGACGACGATGACAAG","siLength":21}'

# Cocktail design
curl -X POST http://localhost:5000/api/cocktail \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGGACTACAAGGACGACGATGACAAG","numTargets":3}'

# AI chemical optimization
curl -X POST http://localhost:5000/api/chem_ai \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGGACTACAAGGACGACGA"}'
```

---

# Appendix A: Glossary

| Term | Definition |
|------|------------|
| **siRNA** | Small Interfering RNA - 21-23 nucleotide RNA duplex |
| **RISC** | RNA-Induced Silencing Complex - cellular machinery that executes RNAi |
| **MFE** | Minimum Free Energy - thermodynamic stability measure |
| **ΔG** | Free Energy Change - negative = favorable reaction |
| **ΔH** | Enthalpy - heat energy of bonding |
| **ΔS** | Entropy - disorder measure |
| **Bloom Filter** | Probabilistic data structure for O(1) membership testing |
| **K-mer** | Substring of length k |
| **CpG** | Cytosine-phosphate-Guanine - immunostimulatory motif |
| **Seed Region** | Positions 2-8 of siRNA - critical for target recognition |
| **Ago2** | Argonaute 2 - catalytic component of RISC |
| **Therapeutic Index** | Balance of stability vs. efficacy |
| **DEG** | Database of Essential Genes |
| **OGEE** | Online GEne Essentiality database |
| **RNAi** | RNA Interference - gene silencing mechanism |

---

# Appendix B: References

1. **SantaLucia, J. (1998)**. A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics. PNAS, 95(4), 1460-1465.

2. **Reynolds, A. et al. (2004)**. Rational siRNA design for RNA interference. Nature Biotechnology, 22(3), 326-330.

3. **Ui-Tei, K. et al. (2004)**. Guidelines for the selection of highly effective siRNA sequences for mammalian and chick RNA interference. Nucleic Acids Research, 32(3), 936-948.

4. **Mathews, D. et al. (1999)**. Expanded nearest-neighbor parameters for predicting duplex free energy. PNAS, 96(9), 4893-4899.

5. **Zhou, J. & Rossi, J. (2017)**. Aptamers as targeted therapeutics: current potential and challenges. Nature Reviews Drug Discovery, 16(3), 181-202.

---

# Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | March 2026 | Initial release |
| 1.1 | March 2026 | Added V8 features |
| 1.2 | March 2026 | Added API reference |

---

**End of Document**

*Helix-Zero V8 :: Regulatory-Grade RNA Interference Design Engine*
*© 2026 Helix-Zero Laboratories*
