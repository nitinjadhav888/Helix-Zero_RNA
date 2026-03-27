# Helix-Zero V8 :: Complete User Workflow & Process Documentation

**Version:** 8.0  
**Date:** March 2026  
**Purpose:** End-to-End Process Guide for Users

---

# Table of Contents

1. [User Goals & Objectives](#1-user-goals--objectives)
2. [Complete Process Flow](#2-complete-process-flow)
3. [Step-by-Step Workflow](#3-step-by-step-workflow)
4. [Model Integration Explained](#4-model-integration-explained)
5. [Output Guide](#5-output-guide)
6. [When to Use Each Feature](#6-when-to-use-each-feature)
7. [Quick Reference](#7-quick-reference)

---

# 1. User Goals & Objectives

## What is the User Trying to Achieve?

As a user of Helix-Zero, you have one primary goal:

> **Design a species-specific RNAi pesticide that kills a pest but is SAFE for beneficial organisms (like honeybees).**

## The Three Pillars of a Good siRNA

For an siRNA to be a successful pesticide, it must satisfy **THREE requirements**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE THREE PILLARS OF siRNA DESIGN                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────┐                                              │
│   │      EFFICACY       │ ← Will it actually kill the pest?            │
│   │      (Does it      │   Can it silence the target gene?           │
│   │       work?)        │                                            │
│   └─────────────────────┘                                            │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────────┐                                              │
│   │       SAFETY        │ ← Will it harm beneficial insects?           │
│   │   (Is it safe to    │   Does it match the bee genome?            │
│   │      pollinators?)   │                                            │
│   └─────────────────────┘                                            │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────────┐                                              │
│   │    STABILITY        │ ← Will it survive in the environment?      │
│   │  (Will it last      │   Can it be chemically modified to last?   │
│   │    long enough?)     │                                            │
│   └─────────────────────┘                                            │
│                                                                          │
│   ALL THREE must be satisfied for a successful RNAi pesticide!           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# 2. Complete Process Flow

## The Complete User Journey

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          HELIX-ZERO COMPLETE WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                         STEP 1: INPUT                                      │
    │  ┌────────────────────┐         ┌────────────────────┐                  │
    │  │ TARGET GENOME       │         │ NON-TARGET GENOME  │                  │
    │  │ (The Pest)          │         │ (The Pollinator)   │                  │
    │  │                     │         │                    │                  │
    │  │ FASTA File:         │         │ FASTA File:         │                  │
    │  │ >pest_gene          │         │ >bee_actin          │                  │
    │  │ ATGCGTACGATCG...    │         │ GATTACAGCTAGT...    │                  │
    │  └────────────────────┘         └────────────────────┘                  │
    │          │                                    │                             │
    └──────────┼────────────────────────────────────┼───────────────────────────┘
               │                                    │
               ▼                                    ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                    STEP 2: CANDIDATE GENERATION                               │
    │                                                                              │
    │   From the pest genome, we generate ALL possible 21-nucleotide sequences:   │
    │                                                                              │
    │   Pest Gene: ATGCGTACGATCGATCGATCGATCGATCGATCGATCGATCG...                 │
    │                  │                                                          │
    │                  ▼                                                          │
    │   ┌─────────────────────────────────────────────────────────────────┐       │
    │   │ Candidate 1: ATGCGTACGATCGATCGATCGA     Position: 1-21        │       │
    │   │ Candidate 2:  TGCGTACGATCGATCGATCGA      Position: 2-22        │       │
    │   │ Candidate 3:   GCGTACGATCGATCGATCGAT      Position: 3-23        │       │
    │   │ Candidate 4:    CGTACGATCGATCGATCGATC      Position: 4-24        │       │
    │   │ ...                                                               │       │
    │   │ (For a 1000bp gene, we get ~980 candidates)                       │       │
    │   └─────────────────────────────────────────────────────────────────┘       │
    └──────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                    STEP 3: SAFETY SCREENING (V6)                            │
    │                                                                              │
    │   Each candidate is checked against the pollinator genome:                   │
    │                                                                              │
    │   ┌─────────────────────────────────────────────────────────────────────┐   │
    │   │                 9-LAYER BIO-SAFETY FIREWALL                          │   │
    │   │                                                                      │   │
    │   │  Layer 1: Does it have 15+ matching bases with the bee?  ──┐      │   │
    │   │  Layer 2: Does it match 21 bases exactly?                  │      │   │
    │   │  Layer 3: Does the seed region (2-8) match?               │      │   │
    │   │  Layer 4: Does it have dangerous secondary structures?        │      │   │
    │   │  Layer 5: Does it have CpG immunogenicity motifs?            │      │   │
    │   │  Layer 6: Is it too repetitive (poly-runs)?                 │      │   │
    │   │  Layer 7: Is the GC content reasonable (30-52%)?            │      │   │
    │   │  Layer 8: Is the thermodynamic profile favorable?            │      │   │
    │   │  Layer 9: Is there internal stability asymmetry?              │      │   │
    │   │                                                             ▼      │   │
    │   │  ┌─────────────────────────────────────────────────────────────┐ │   │
    │   │  │  SAFETY SCORE: 0-100                                      │ │   │
    │   │  │  >85 = SAFE for pollinators    <85 = UNSAFE               │ │   │
    │   │  └─────────────────────────────────────────────────────────────┘ │   │
    │   └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                    STEP 4: EFFICACY PREDICTION (V7)                         │
    │                                                                              │
    │   For SAFE candidates, predict how well they will silence the pest:         │
    │                                                                              │
    │   ┌─────────────────────────────────────────────────────────────────────┐   │
    │   │                  RiNALMo-v2 DEEP LEARNING MODEL                       │   │
    │   │                                                                      │   │
    │   │   Input: ATGCGTACGATCGATCGATCGA (safe sequence)                      │   │
    │   │              │                                                        │   │
    │   │              ▼                                                        │   │
    │   │   ┌──────────────────────────────────────────────────────────────┐ │   │
    │   │   │  1. K-mer Embedding (learns sequence patterns)              │ │   │
    │   │   │  2. Transformer Attention (finds important features)         │ │   │
    │   │   │  3. Physics Features (adds thermodynamic rules)            │ │   │
    │   │   │  4. Hybrid Ensemble (combines everything)                   │ │   │
    │   │   └──────────────────────────────────────────────────────────────┘ │   │
    │   │              │                                                        │   │
    │   │              ▼                                                        │   │
    │   │   ┌──────────────────────────────────────────────────────────────┐ │   │
    │   │   │  EFFICACY SCORE: 0-100%                                       │ │   │
    │   │   │  >85% = Highly effective    <60% = Poor                     │ │   │
    │   │   └──────────────────────────────────────────────────────────────┘ │   │
    │   └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                    STEP 5: RANKING & FILTERING                              │
    │                                                                              │
    │   Combine safety + efficacy into a COMPOSITE SCORE:                          │
    │                                                                              │
    │   ┌─────────────────────────────────────────────────────────────────────┐   │
    │   │                                                                      │   │
    │   │   Composite = (Safety × 0.4) + (Efficacy × 0.3) + (Essentiality × 0.3)  │
    │   │                                                                      │   │
    │   │   Example:                                                          │   │
    │   │   Safety: 95% × 0.4 = 38.0                                          │   │
    │   │   Efficacy: 88% × 0.3 = 26.4                                          │   │
    │   │   Essentiality: 90% × 0.3 = 27.0                                      │   │
    │   │   ───────────────────────────────                                       │   │
    │   │   Composite Score: 91.4                                                │   │
    │   │                                                                      │   │
    │   └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                              │
    │   Candidates are ranked by composite score (highest first)                   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                    STEP 6: V8 ADVANCED FEATURES                              │
    │                                                                              │
    │   Optional enhancements for the TOP CANDIDATES:                              │
    │                                                                              │
    │   ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────────┐   │
    │   │  COCKTAIL DESIGN   │  │  AI CHEM OPTIMIZE  │  │  RNA STRUCTURE 🆕    │   │
    │   │                    │  │                    │  │                        │   │
    │   │ Design 3 siRNAs   │  │ Add chemical      │  │ Visualize 2D        │   │
    │   │ that target        │  │ modifications     │  │ folding: hairpins,  │   │
    │   │ different parts     │  │ to make it        │  │ loops, stems        │   │
    │   │ of the gene        │  │ more stable      │  │                      │   │
    │   └────────────────────┘  └────────────────────┘  └────────────────────────┘   │
    │                                                                              │
    │   ┌────────────────────┐  ┌────────────────────┐                              │
    │   │  RNA ACCESSIBILITY │  │  TISSUE FILTER    │                              │
    │   │                    │  │                    │                              │
    │   │ Thermodynamic      │  │ Filter by         │                              │
    │   │ analysis of       │  │ delivery tissue   │                              │
    │   │ target site       │  │ expression        │                              │
    │   └────────────────────┘  └────────────────────┘                              │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                    STEP 7: OUTPUT & RESULTS                                 │
    │                                                                              │
    │   ┌─────────────────────────────────────────────────────────────────────┐   │
    │   │                                                                      │   │
    │   │   TOP siRNA CANDIDATES:                                              │   │
    │   │                                                                      │   │
    │   │   ┌──────────────────────────────────────────────────────────────┐ │   │
    │   │   │ Rank 1: ATGCGTACGATCGATCGATCGA                                 │ │   │
    │   │   │ Safety: 98.5%  Efficacy: 91.2%  Composite: 94.8%           │ │   │
    │   │   └──────────────────────────────────────────────────────────────┘ │   │
    │   │   ┌──────────────────────────────────────────────────────────────┐ │   │
    │   │   │ Rank 2: TGCGTACGATCGATCGATCGAT                               │ │   │
    │   │   │ Safety: 97.2%  Efficacy: 89.5%  Composite: 93.1%            │ │   │
    │   │   └──────────────────────────────────────────────────────────────┘ │   │
    │   │   ...                                                              │   │
    │   │                                                                      │   │
    │   │   [+ Download CSV]  [+ View Certificate]  [+ Design Cocktail]     │   │
    │   │                                                                      │   │
    │   └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                    STEP 8: CERTIFICATE GENERATION                            │
    │                                                                              │
    │   For the top candidate, generate a regulatory-grade safety certificate:    │
    │                                                                              │
    │   ┌─────────────────────────────────────────────────────────────────────┐   │
    │   │              🏆 HELIX-ZERO CERTIFICATE OF BIOLOGICAL SAFETY          │   │
    │   │                                                                      │   │
    │   │   Sequence: ATGCGTACGATCGATCGATCGA                                 │   │
    │   │   Safety Score: 98.5%                                               │   │
    │   │   Efficacy Score: 91.2%                                              │   │
    │   │   Certificate ID: A7B3C9D2E1                                        │   │
    │   │   Status: ✅ CLEARED FOR REGULATORY USE                             │   │
    │   │                                                                      │   │
    │   └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

                    🎉 PIPELINE COMPLETE! 🎉
```

---

# 3. Step-by-Step Workflow

## User's Perspective

### Step 1: User Provides Inputs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  INPUT 1: TARGET GENOME (The Pest)                                          │
│  ─────────────────────────────────                                          │
│  What: FASTA file containing the pest's genome or gene sequence             │
│  Why: We need to find potential silencing targets in the pest              │
│  How: Upload .fasta or .txt file                                           │
│                                                                             │
│  Example:                                                                   │
│  >fall_armyworm_chitinase                                                  │
│  ATGCGTACGATCGATCGATCGATCGATCGATCGATCGATCGATCG...                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT 2: NON-TARGET GENOME (The Pollinator)                               │
│  ─────────────────────────────────────                                      │
│  What: FASTA file containing the pollinator's genome (e.g., honeybee)     │
│  Why: To ensure our siRNA doesn't harm the pollinator                      │
│  How: Upload .fasta or .txt file                                           │
│                                                                             │
│  Example:                                                                   │
│  >apis_mellifera_actin                                                     │
│  GATTACAGCTAGTCGATCGATCGATCGATCGATCGATCGATCG...                           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT 3: TARGET GENE NAME (Optional)                                      │
│  ─────────────────────────────────                                         │
│  What: Name of the gene you want to silence (e.g., "chitinase")          │
│  Why: For essentiality scoring - is this gene critical for the pest?        │
│  How: Type in the gene name field                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step 2: User Clicks "RUN DL PIPELINE"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  WHAT HAPPENS:                                                             │
│  ─────────────                                                             │
│                                                                             │
│  1. System generates all 21-nt candidates from the pest sequence           │
│                                                                             │
│  2. Each candidate is checked against the pollinator genome:                │
│     • Does it have 15+ matching bases?                                     │
│     • Does the seed region match?                                           │
│     • Does it have dangerous structures?                                     │
│                                                                             │
│  3. Safe candidates are scored for efficacy using RiNALMo-v2               │
│                                                                             │
│  4. All candidates are ranked by composite score                           │
│                                                                             │
│  WHAT THE USER SEES:                                                       │
│  ──────────────────                                                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Scanning candidates... ████████████░░░░░░░░ 70%                     │   │
│  │                                                                     │   │
│  │  500 candidates generated...                                         │   │
│  │  320 passed safety screening...                                     │   │
│  │  Analyzing efficacy with RiNALMo-v2...                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step 3: User Reviews Results

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  RESULTS TABLE:                                                             │
│  ─────────────                                                             │
│                                                                             │
│  ┌──────┬────────────────────────┬────────┬─────────┬────────┬──────────┐ │
│  │ Rank │ Sequence               │ Safety │ Efficacy│ GC%   │ Status   │ │
│  ├──────┼────────────────────────┼────────┼─────────┼────────┼──────────┤ │
│  │  1   │ ATGCGTACGATCGATCGATCGA│  98.5% │  91.2%  │  47.6% │ CLEARED  │ │
│  │  2   │ TGCGTACGATCGATCGATCGA │  97.2% │  89.5%  │  47.6% │ CLEARED  │ │
│  │  3   │ GCGTACGATCGATCGATCGA  │  95.8% │  88.1%  │  42.9% │ CLEARED  │ │
│  │  4   │ CGTACGATCGATCGATCGATC │  85.2% │  85.0%  │  38.1% │ REVIEW   │ │
│  │  5   │ GTACGATCGATCGATCGATCG │  45.3% │  78.2%  │  33.3% │ REJECTED │ │
│  └──────┴────────────────────────┴────────┴─────────┴────────┴──────────┘ │
│                                                                             │
│  KPIs:                                                                     │
│  ─────                                                                     │
│  Candidates Scanned: 500                                                    │
│  High Efficacy (>90%): 12                                                  │
│  Average Efficacy: 78.5%                                                    │
│  Rejection Rate: 36%                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step 4: User Uses V8 Advanced Features (Optional)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  FOR THE TOP CANDIDATE, THE USER CAN:                                       │
│  ────────────────────────────────                                           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ OPTION A: Design Multi-Target Cocktail                               │ │
│  │                                                                       │ │
│  │ Click: "Design Multi-Target Cocktail"                                 │ │
│  │ Result: 3 non-overlapping siRNAs that target different regions        │ │
│  │ Why: Prevents pest resistance (would need 3 mutations to escape)     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ OPTION B: AI Chemical Optimization                                    │ │
│  │                                                                       │ │
│  │ Click: "AI Chemical Optimization"                                     │ │
│  │ Result: Best modification pattern (2'-OMe, 2'-F, or PS)               │ │
│  │ Why: Makes the siRNA last longer in the environment                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ OPTION C: RNA Accessibility Check                                     │ │
│  │                                                                       │ │
│  │ Click: "RNA Accessibility Check"                                       │ │
│  │ Result: Is the target site accessible to RISC?                       │ │
│  │ Why: Even perfect siRNA fails if target is buried in mRNA structure │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step 5: User Downloads Results

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  DOWNLOAD OPTIONS:                                                           │
│  ───────────────                                                            │
│                                                                             │
│  1. CSV Export                                                              │
│     All candidates with full details                                         │
│     Columns: Rank, Sequence, Safety, Efficacy, GC, MFE, Asymmetry, etc.    │
│                                                                             │
│  2. Safety Certificate (PDF)                                               │
│     Regulatory-grade document for top candidate                              │
│     Includes all 9 safety layer details                                     │
│                                                                             │
│  3. Cocktail Design Report (if cocktail was generated)                      │
│     3 siRNAs with synergy scores                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 4. Model Integration Explained

## How Different Models Work Together

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MODEL INTEGRATION FLOWCHART                              │
└─────────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   USER INPUT    │
                           │  Target Genome │
                           │ Non-Target Gen │
                           └────────┬────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     V6 ENGINE (Safety)       │
                    │                               │
                    │  ┌─────────────────────────┐ │
                    │  │ 9-Layer Bio-Safety     │ │
                    │  │ Firewall               │ │
                    │  │                        │ │
                    │  │ - 15-mer exclusion    │ │
                    │  │ - Seed region match   │ │
                    │  │ - CpG motifs         │ │
                    │  │ - GC content         │ │
                    │  │ - Palindromes        │ │
                    │  │ - Poly-runs          │ │
                    │  │ - Thermodynamics      │ │
                    │  └─────────────────────────┘ │
                    │                               │
                    │  OUTPUT: Safety Score (0-100) │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     FILTER: Safety > 70%       │
                    │                               │
                    │   Only safe candidates proceed  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  V7 MODEL (Efficacy)          │
                    │                               │
                    │  ┌─────────────────────────┐ │
                    │  │  RiNALMo-v2 Transformer  │ │
                    │  │                         │ │
                    │  │  - K-mer embeddings     │ │
                    │  │  - Self-attention      │ │
                    │  │  - Physics features     │ │
                    │  │  - Hybrid ensemble     │ │
                    │  └─────────────────────────┘ │
                    │                               │
                    │  OUTPUT: Efficacy Score (0-100)│
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  ESSENTIALITY SCORING         │
                    │                               │
                    │  - DEG database match          │
                    │  - OGEE conservation          │
                    │  - RNAi phenotype              │
                    │                               │
                    │  OUTPUT: Essentiality (0-100)  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  COMPOSITE SCORING             │
                    │                               │
                    │  Composite =                  │
                    │  Safety × 0.4 +               │
                    │  Efficacy × 0.3 +             │
                    │  Essentiality × 0.3           │
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     RANKING & OUTPUT           │
                    │                               │
                    │  Top candidates sorted by      │
                    │  composite score              │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   COCKTAIL   │          │  AI CHEM     │          │  RNA ACCESS  │
│   DESIGN     │          │  OPTIMIZE    │          │  CHECK      │
│   (V8)       │          │   (V8)       │          │   (V8)       │
│               │          │               │          │              │
│ Design 3     │          │ Monte-Carlo  │          │ Thermodynamic│
│ non-overlap  │          │ search for   │          │ analysis of  │
│ siRNAs       │          │ best mod    │          │ target site  │
│               │          │ pattern     │          │ accessibility│
└───────────────┘          └───────────────┘          └───────────────┘
```

## When Each Model is Used

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODEL USAGE TIMELINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STAGE 1: Initial Screening (AUTOMATIC)                                      │
│  ═══════════════════════════════                                             │
│                                                                             │
│  Model: V6 Engine (Safety Firewall)                                         │
│  When: Always, on every candidate                                            │
│  Purpose: Filter out unsafe candidates                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │   1000 candidates → V6 Engine → 350 safe candidates                  │ │
│  │                                                                     │ │
│  │   Rejected: 650 (65%)                                               │ │
│  │   - 200 had 15+ homology matches                                     │ │
│  │   - 150 had CpG motifs                                              │ │
│  │   - 120 had poly-runs                                               │ │
│  │   - 180 had poor GC content                                         │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STAGE 2: Efficacy Prediction (AUTOMATIC)                                    │
│  ═══════════════════════════════════                                        │
│                                                                             │
│  Model: V7 RiNALMo-v2                                                      │
│  When: On all candidates that passed V6                                     │
│  Purpose: Predict how well each candidate will work                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │   350 safe candidates → RiNALMo-v2 → Efficacy scores                │ │
│  │                                                                     │ │
│  │   High (>85%): 45 candidates                                        │ │
│  │   Medium (70-85%): 180 candidates                                  │ │
│  │   Low (<70%): 125 candidates                                        │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STAGE 3: V8 Advanced Features (ON-DEMAND)                                  │
│  ════════════════════════════════════════════════                           │
│                                                                             │
│  Model: V8 Advanced Modules                                                 │
│  When: User clicks specific buttons                                          │
│  Purpose: Enhance/optimize the best candidates                              │
│                                                                             │
│  Click "Cocktail Design"    → Cocktail module runs                         │
│  Click "AI Chemical Opt"    → Chem AI module runs                           │
│  Click "RNA Accessibility" → Accessibility module runs                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Integration Priority

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTEGRATION PRIORITY & DEPENDENCIES                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  REQUIRED (Always runs):                                                    │
│  ────────────────────────────                                               │
│  1. V6 Engine (Safety)     ← FILTERS candidates first                     │
│  2. V7 RiNALMo-v2 (Efficacy) ← SCORES remaining candidates                  │
│  3. Essentiality Scoring    ← RANKS by biological importance                  │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│  OPTIONAL (User requests):                                                 │
│  ─────────────────────────                                                  │
│  4. Cocktail Design        ← Needs V6+V7 output                            │
│  5. AI Chemical Optimize  ← Needs single sequence                           │
│  6. RNA Accessibility     ← Needs single sequence                           │
│  7. Tissue Filter        ← Needs off-target list                          │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│  EXECUTION ORDER:                                                          │
│  ─────────────────                                                         │
│                                                                             │
│  [Input] → [V6 Safety] → [V7 Efficacy] → [Essentiality] → [Composite]   │
│       │                                                                 │
│       └─────────────────────────────────────────────────────────────────── │
│                                   │                                        │
│                    ┌──────────────┼──────────────┐                         │
│                    ▼              ▼              ▼                         │
│              [Cocktail]     [AI Chem]     [RNA Access]                     │
│              (Optional)    (Optional)    (Optional)                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 5. Output Guide

## What Each Output Means

### Safety Score

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SAFETY SCORE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  What it is: How safe the siRNA is for pollinators                         │
│                                                                             │
│  Range: 0-100%                                                             │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │  85-100%: ✅ CLEARED - Safe for pollinators                          │ │
│  │  70-84%:  ⚠️ REVIEW - May need manual inspection                     │ │
│  │  50-69%:  ⚠️ CAUTION - Significant safety concerns                 │ │
│  │  0-49%:   ❌ REJECTED - Unsafe, do not use                          │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  How it's calculated:                                                       │
│  • Starts at 100%                                                          │
│  • 15-mer match found: -15 to -100 points                                 │
│  • CpG motif found: -20 points                                             │
│  • Poly-run found: -25 points                                              │
│  • Poor GC content: -8 to -15 points                                      │
│  • Seed region match: -5 to -30 points                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Efficacy Score

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EFFICACY SCORE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  What it is: How well the siRNA will silence the target gene               │
│                                                                             │
│  Range: 0-100%                                                             │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │  85-100%: ⭐ EXCELLENT - Highly effective silencing                  │ │
│  │  70-84%:  ✅ GOOD - Should work well                                │ │
│  │  50-69%:  ⚠️ MODERATE - May have reduced effect                    │ │
│  │  0-49%:   ❌ POOR - Likely ineffective                              │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  How it's calculated (RiNALMo-v2):                                         │
│  • Position-specific nucleotide preferences                                  │
│  • GC content optimization                                                 │
│  • Thermodynamic stability                                                  │
│  • Dinucleotide composition                                                 │
│  • Deep learning pattern recognition                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Composite Score

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            COMPOSITE SCORE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  What it is: Overall ranking of candidate quality                           │
│                                                                             │
│  Formula:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   Composite = (Safety × 0.4) + (Efficacy × 0.3) + (Essentiality × 0.3)  │
│  │                                                                     │   │
│  │   Example:                                                          │   │
│  │   Safety: 95% × 0.4 = 38.0                                         │   │
│  │   Efficacy: 88% × 0.3 = 26.4                                         │   │
│  │   Essentiality: 90% × 0.3 = 27.0                                     │   │
│  │   ─────────────────────────────────                                  │   │
│  │   Composite Score: 91.4                                               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Interpretation:                                                            │
│  • 90-100%: 🌟 TOP CHOICE - Excellent across all metrics                  │
│  • 80-89%:  ✅ RECOMMENDED - Good balance                                 │
│  • 70-79%:  ⚠️ ACCEPTABLE - May need optimization                       │
│  • <70%:    ❌ NOT RECOMMENDED - Significant issues                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 6. When to Use Each Feature

## Decision Guide

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     WHEN TO USE EACH FEATURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ BASIC PIPELINE (Always)                                              │   │
│  │                                                                     │   │
│  │ Use: V6 + V7 + Essentiality                                        │   │
│  │ When: First time screening                                          │   │
│  │ Output: Ranked list of candidates                                   │   │
│  │                                                                     │   │
│  │ This is the DEFAULT - runs automatically when you click             │   │
│  │ "RUN DL PIPELINE"                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ COCKTAIL DESIGN (For Resistance Prevention)                         │   │
│  │                                                                     │   │
│  │ Use: V8 Cocktail Module                                            │   │
│  │ When: You need a robust solution that won't be evaded               │   │
│  │ Output: 3 non-overlapping siRNAs                                    │   │
│  │                                                                     │   │
│  │ Example Scenario:                                                   │   │
│  │ "I want to make sure the pest can't develop resistance              │   │
│  │  by mutating a single base."                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ AI CHEMICAL OPTIMIZATION (For Stability)                            │   │
│  │                                                                     │   │
│  │ Use: V8 AI Chem Module                                              │   │
│  │ When: You need the siRNA to last longer in the environment         │   │
│  │ Output: Optimized modification pattern                               │   │
│  │                                                                     │   │
│  │ Example Scenario:                                                   │   │
│  │ "The siRNA needs to survive in the field for days, not hours."     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ RNA STRUCTURE PREDICTION (For Visualization) 🆕                       │   │
│  │                                                                     │   │
│  │ Use: V8 RNA Structure Module                                        │   │
│  │ When: You want to SEE the actual 2D folding of the RNA            │   │
│  │ Output: ASCII visualization, dot-bracket notation, elements         │   │
│  │                                                                     │   │
│  │ Example Scenario:                                                   │   │
│  │ "I want to see if there are hairpins or loops that might         │   │
│  │  affect siRNA binding."                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ RNA ACCESSIBILITY CHECK (For Confidence)                             │   │
│  │                                                                     │   │
│  │ Use: V8 RNA Access Module                                           │   │
│  │ When: You want to verify the target site is accessible             │   │
│  │ Output: Accessibility score and classification                      │   │
│  │                                                                     │   │
│  │ Example Scenario:                                                   │   │
│  │ "Even with good efficacy, I'm worried the mRNA structure          │   │
│  │  might block the siRNA from binding."                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ TISSUE FILTER (For Precision Medicine)                             │   │
│  │                                                                     │   │
│  │ Use: V8 Tissue Module                                              │   │
│  │ When: You want to filter by delivery tissue                        │   │
│  │ Output: Threat levels based on tissue-specific expression           │   │
│  │                                                                     │   │
│  │ Example Scenario:                                                   │   │
│  │ "Our siRNA is delivered to the liver, so off-target genes          │   │
│  │  expressed in other tissues don't matter."                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Feature Comparison

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            FEATURE COMPARISON                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┬─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │ Feature       │ Input       │ Output      │ Use Case    │ Time        │ │
│  ├──────────────┼─────────────┼─────────────┼─────────────┼─────────────┤ │
│  │ V6 Safety     │ Sequence    │ 0-100       │ Mandatory   │ <1 sec     │ │
│  │ V7 Efficacy    │ Sequence    │ 0-100       │ Mandatory   │ <1 sec     │ │
│  │ Essentiality   │ Gene Name   │ 0-100       │ Recommended │ <1 sec     │ │
│  ├──────────────┼─────────────┼─────────────┼─────────────┼─────────────┤ │
│  │ RNA Structure │ 1 siRNA     │ ASCII Viz   │ Visualize  │ <1 sec     │ │
│  │ Cocktail      │ Gene        │ 3 siRNAs    │ Resistance  │ 2-5 sec    │ │
│  │ AI Chem       │ 1 siRNA     │ Mod pattern │ Stability   │ 5-10 sec   │ │
│  │ RNA Access     │ 1 siRNA     │ Score+Class │ Confidence  │ <1 sec     │ │
│  │ Tissue Filter  │ Gene list   │ Threat lvls │ Precision   │ <1 sec     │ │
│  └──────────────┴─────────────┴─────────────┴─────────────┴─────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 7. Quick Reference

## Complete Process Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUICK REFERENCE CARD                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. INPUT                                                                   │
│     • Target genome (FASTA) - What you want to kill                        │
│     • Non-target genome (FASTA) - Who you want to protect                   │
│     • Gene name (optional) - For essentiality scoring                       │
│                                                                             │
│  2. PROCESS                                                                 │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │ Step 1: Generate all 21-nt candidates from target              │     │
│     │ Step 2: V6 checks safety against non-target                      │     │
│     │ Step 3: V7 predicts efficacy of safe candidates                  │     │
│     │ Step 4: Rank by composite score                                  │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  3. OUTPUT                                                                  │
│     • Ranked table of candidates                                            │
│     • Safety scores (should be >85%)                                        │
│     • Efficacy scores (should be >70%)                                       │
│     • Composite scores (higher is better)                                    │
│     • Safety certificate for top candidate                                   │
│                                                                             │
│  4. OPTIONAL ENHANCEMENTS                                                  │
│     • Cocktail: 3 siRNAs targeting different regions                        │
│     • AI Chem: Best chemical modification pattern                           │
│     • RNA Access: Verify target site accessibility                          │
│     • Tissue Filter: Filter by tissue-specific expression                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  REMEMBER:                                                                  │
│  • Always run V6 + V7 first (automatic)                                    │
│  • Use V8 features on top candidates only                                  │
│  • Cocktail is best for preventing resistance                              │
│  • AI Chem is best for environmental stability                              │
│  • RNA Access builds confidence in target selection                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## API Call Order

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API CALL SEQUENCE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AUTOMATIC (when "RUN DL PIPELINE" is clicked):                           │
│  ════════════════════════════════════════════════════════                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  1. POST /api/first_model                                         │   │
│  │     → Runs V6 (Safety) + Essentiality                             │   │
│  │     → Returns all candidates with safety scores                     │   │
│  │                                                                     │   │
│  │  2. POST /api/predict (to FastAPI port 8000)                      │   │
│  │     → Runs V7 (RiNALMo-v2 Efficacy)                              │   │
│  │     → Returns efficacy predictions                                  │   │
│  │                                                                     │   │
│  │  3. Results are merged, sorted by composite score                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ON-DEMAND (when user clicks specific buttons):                            │
│  ════════════════════════════════════════════════════                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  POST /api/cocktail                                                │   │
│  │  → Requires: sequence + gene name                                  │   │
│  │  → Returns: 3 non-overlapping siRNAs                              │   │
│  │                                                                     │   │
│  │  POST /api/chem_ai                                                 │   │
│  │  → Requires: single sequence                                       │   │
│  │  → Returns: best modification pattern                              │   │
│  │                                                                     │   │
│  │  POST /api/rna_accessibility                                       │   │
│  │  → Requires: single sequence                                       │   │
│  │  → Returns: accessibility score                                     │   │
│  │                                                                     │   │
│  │  POST /api/tissue_filter                                           │   │
│  │  → Requires: sequence + gene list + tissue                         │   │
│  │  → Returns: threat levels                                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Document Version

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | March 2026 | Helix-Zero | Initial release |

---

**End of Document**

*This document explains the complete user workflow for Helix-Zero V8*
