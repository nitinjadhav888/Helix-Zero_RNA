# Helix-Zero: Next-Generation Molecular Engineering Suite Roadmap

## Strategic Overview
The provided vision outlines the transition of Helix-Zero V7 from a computational discovery tool into an enterprise-grade **Molecular Engineering Suite**. This requires shifting from deterministic formulas to predictive AI models, simulating chemical stability, and deploying scalable backend architecture.

Based on the existing V7 implementation (which already has robust parsing, a 15-mer firewall, essentiality scoring, and basic thermodynamics), here is a realistic, structured plan for further implementation.

## User Review Required
> [!IMPORTANT]
> **Architecture Shift:** Implementing deep learning (OligoGraph/RiNALMo) and 3D molecular predictions (Chai-Lab/GROMACS) **cannot** be done solely in the browser using React/TypeScript. We will need to decide if we want to build a dedicated Python/Docker backend API first, or mock these capabilities in TypeScript while building the backend in parallel.
> Please review the proposed architecture in Phase 4.

---

## Phase 1: Deep-Learning Based Efficacy Prediction
*Current State:* Efficacy is calculated deterministically using Reynolds/Ui-Tei rules via `calculatePositionScore` and `calculateAsymmetry`.\
*Goal:* Replace rule-based scoring with Structural Graph Neural Networks and Language Models.

### 1.1 OligoGraph / RiNALMo Integration
* **Implementation:** Create a Python-based microservice (`ml-predictor-api`) that loads pre-trained RNA Language Models.
* **TypeScript Updates:** Modify `src/lib/engine.ts` (`predictEfficacy` function) to make an asynchronous fetch request to this new API instead of using the hardcoded weighting algorithm.
* **Realistic Timeline:** Medium. Open-source RNA foundation models exist (e.g., RNA-FM), but fine-tuning them for siRNA efficacy will require curating a training dataset.

### 1.2 Automated Thermodynamic Asymmetry & MFE (ViennaRNA)
* **Current State:** V7 already implements a simplified MFE calculation (`rnaStructureModeler.ts`).
* **Implementation:** Upgrade `rnaStructureModeler.ts` to use WebAssembly binaries of ViennaRNA (`RNAfold`) so it runs natively in the browser without server overhead, calculating the exact Differential Duplex-End Stability and target site accessibility.

---

## Phase 2: Advanced Structural & Chemical Optimization
*Current State:* No chemical modification modeling exists.\
*Goal:* Simulate "Chemical Armor" (sugar modifications, backbones) to survive enzymatic degradation.

### 2.1 Chemical Modification Simulator (CMS)
* **Implementation:** Create a new module `src/lib/optimization/chemicalSimulator.ts`.
* **Features:** 
    * Allow users to select modification patterns (2'-OMe, 2'-F) via the UI in `SiRNADesigner.tsx`.
    * Calculate a "Stability Half-Life Score" that estimates how long the siRNA survives in the field.
    * Add logic to penalize over-modification (which reduces Ago2 binding affinity).
* **Realistic Timeline:** Fast. This can be implemented using deterministic scoring models based on existing literature for 2'-OMe/2'-F impact.

### 2.2 3D Molecular Fingerprinting (Ago2 Complex Modeling)
* **Implementation:** Highly complex. Requires setting up Chai-Lab or AlphaFold3 models on GPU-enabled cloud instances. 
* **UI Integration:** Helix-Zero would send the modified siRNA sequence to the backend, which returns a 3D structural file (.pdb). The React frontend would use a specialized library (like `molstar` or `3dmol.js`) to render the siRNA-Ago2 complex directly in the browser.

---

## Phase 3: The "9-Layer" Safety & Risk Firewall
*Current State:* V7 has a 5-layer firewall including 15-mer exclusion, seed match, palindromes, and basic motifs.\
*Goal:* Expand to regulatory-standard 9-layer Bioinformatic Framework.

### 3.1 Strict 21-nt Identity Screen & Enhanced Firewall
* **Implementation:** Upgrade `enhancedFirewall.ts` to explicitly log absolute 21-nt matches across non-target transcriptomes.
* **Immune Motifs:** Expand the existing `IMMUNE_STIMULATING_MOTIFS` array in `engine.ts` to include patterns like `UGUGU` and comprehensive CpG island detectors.

### 3.2 Phylogenetic Ortholog Analysis
* **Implementation:** Expand `conservationAnalyzer.ts` (Module 4) to automatically map targets across the taxonomic tree. 
* **UI Integration:** Add a "Taxonomic Scope" visualizer (like a phylogenetic tree graph) in the `LaboratoryReportView` that highlights which evolutionary branches might be susceptible to off-target effects.

---

## Phase 4: Resistance & Durability Modeling
*Current State:* V7 has `resistanceEvolution.ts` covering basic fitness cost and escape mutant calculations.\
*Goal:* Forecast the "Resistance Timeline" and automate cocktail design.

### 4.1 Mutation Hotspot & Cocktail Design
* **Implementation:** Enhance `resistanceEvolution.ts` to fetch SNP data or calculate sequence Shannon Entropy. Identify robust regions.
* **Network Propagation:** In `essentialGeneFilter.ts`, use PPI network graphs to find pairs of genes that, if silenced together, cause synthetic lethality. Create a new `Multi-Target Cocktail` tab in the UI that spits out 2-3 siRNAs designed to work synergistically.

---

## Technical Architecture & Implementation Overhaul

To support these advanced features, the underlying architecture must evolve:

### 1. Hybrid Backend System (Docker + Python)
* Keep the lightning-fast Vite/React frontend for UI and lightweight tasks.
* Build a RESTful Python API (`helix-engine-core`) packaged in Docker for structural simulations (GROMACS, Chai-Lab) and deep learning predictions.

### 2. High-Performance Indexing (24-bit Genomes)
* **Implementation:** Upgrade `bloomFilter.ts`. Instead of storing sequences as strings which crash JS heaps at >500MB, implement a `Uint8Array` based 2-bit or 3-bit encoding system in WebAssembly or structured arrays to compress genome memory usage by 75-80%.

### 3. Web Worker Parallelization
* **Implementation:** Move safety screening computations into Web Workers (`src/workers/safetyWorker.ts`). 
* **Benefit:** When screening against the 20-species Non-Target Panel, the main React thread won't freeze, allowing smooth UI performance during heavy computational loads.
