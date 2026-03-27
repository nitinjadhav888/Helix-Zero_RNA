# siRNA Structure and Modification Prediction: Research & Integration Plan

## 1. Overview
This document details the integration of RNA secondary structure prediction into the Helix-Zero CMS pipeline. The goal is to predict and visualize the folding of both native and chemically modified siRNA guide strands to identify potential self-structure issues (hairpins) that could inhibit RISC loading.

## 2. Scientific Basis & Citations

### 2.1 Native Structure Prediction
Standard RNA folding is often predicted using Minimum Free Energy (MFE) algorithms based on Nearest Neighbor parameters.

*   **Algorithm**: Dynamic Programming (Zuker & Stiegler).
*   **Parameters**: Turner 2004 energy parameters.
*   **Citation**: 
    *   *Lorenz, R. et al. (2011).* "ViennaRNA Package 2.0". Algorithms for Molecular Biology, 6:26.
    *   *Mathews, D. H. et al. (2004).* "Incorporating chemical modification constraints into a dynamic programming algorithm for prediction of RNA secondary structure". PNAS.

### 2.2 Impact of Chemical Modifications
Chemical modifications (2'-OMe, 2'-F, PS) alter the thermodynamic stability of base pairs. 
*   **2'-O-methyl (2'-OMe)**: Generally stabilizes RNA-RNA duplexes (increases Tm).
*   **2'-Fluoro (2'-F)**: Significantly stabilizes helical structure.
*   **Phosphorothioate (PS)**: Slightly destabilizes structure but adds nuclease resistance.

*   **Citation**: 
    *   *Wan, Y. et al. (2011).* "Landscape and variation of RNA secondary structure across the human transcriptome". Nature. (Discusses structural probing).
    *   *Setten, R.L. et al. (2019).* "The current state of oligonucleotide therapeutics". Nature Reviews Drug Discovery.

## 3. Implementation Strategy

### 3.1 Tool Selection: ViennaRNA (via Python) vs. Heuristic Fallback
To ensure cross-platform compatibility (especially on Windows where compiling ViennaRNA is difficult), we implement a hybrid approach:

1.  **Primary**: Try to import `RNA` (ViennaRNA Python bindings) if available.
2.  **Fallback**: Implement a pure-Python **Nussinov algorithm** (Maximum Matching) or a simplified **Zuker-like MFE** calculator using the existing thermodynamics engine in `calculations.py`.

### 3.2 Visualization
We will use **FornaContainer** (based on ViennaRNA's forna) for interactive 2D visualization in the web dashboard.
*   **Citation**: *Kerpedjiev, P. et al. (2015).* "Forna: a tool for the visualization of secondary structure of RNA". Bioinformatics.

## 4. Pipeline Integration

### 4.1 New Module: `src/structure.py`
A new module responsible for:
*   Generating Dot-Bracket notation (e.g., `((...))...`).
*   Calculating Free Energy ($ \Delta G $).
*   Applying modification penalties/boosts to the energy score.

### 4.2 Dashboard Update
*   Add a "Structure" tab/panel.
*   Render the structure using Forna (JS).
*   Display Native vs. Modified folding propensity.

## 5. Modified RNA Logic
Since standard tools often predict backbone geometry, we simulate "Modified" structure by applying energy bonus terms to modified positions during the scoring phase, effectively creating a "Weighted MFE".

*   *Hypothesis*: If a modification (e.g., 2'-F) is inside a stem, it stabilizes it. If a bulky modification is sterically hindering, it destabilizes.
*   *Implementation*: We will highlight modified bases in the visualization to allow visual inspection of their location relative to hairpins. (e.g. A modification in a loop is good; in a stem might prevent unwinding).
