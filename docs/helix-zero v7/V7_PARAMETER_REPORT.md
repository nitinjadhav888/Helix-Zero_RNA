# Helix-Zero V7: Parameter Generation & Implementation Report

This document exhaustively breaks down the mathematical logic and exact implementation behind every parameter generated in the **V7 Module 7 (Enhanced Safety)** and **Module 8 (Resistance Evolution)** pipelines.

None of these outputs are mocked; they are generated dynamically by scanning the thermodynamic and sequence profile of the generated siRNA against specific biological scoring algorithms.

---

## 1. Module 7: Enhanced Safety Firewall

This module is handled entirely by `src/lib/safety/enhancedFirewall.ts`. The inputs are the raw siRNA sequence, a non-target transcriptome, and target species profiles.

### A. miRNA Off-Target Risk
**Output:** `LOW`, `MEDIUM`, or `HIGH`
**Background:** Human and insect cells use microRNAs (miRNAs) to regulate gene expression naturally. If our designed siRNA mimics an existing miRNA, it will inadvertently shut down vital physiological functions off-target.
**Implementation Logic:**
1. The engine strips out positions 2-8 of the designed siRNA. This is called the "Seed Region".
2. It cross-references this 7-base sequence against a database of known highly-regulated miRNA seed families (such as `let-7` (`AGCUGAU`), `miR-124`, `miR-122`, etc.).
3. **Scoring:** 
   - 0 matches = **LOW**
   - Exactly 1 match = **MEDIUM**
   - >1 matches = **HIGH**

### B. Complementarity Risk
**Output:** Percentage (0-100%)
**Background:** Indicates the highest degree of accidental binding to a beneficial non-target species.
**Implementation Logic:**
1. The engine iterates through the uploaded "Non-Target Transcripts" database (e.g., Honeybee transcriptome).
2. It counts the maximal contiguous Watson-Crick complementary bases between the siRNA and the non-target mRNA.
3. **Scoring:** The mathematical score is explicitly calculated as `Math.min(100, (Max_Complementary_Bases / 21) * 100)`. Thus, a 50% score indicates roughly 10 matches.

### C. Immune Stimulation Score
**Output:** Percentage (0-100%)
**Background:** Unmodified RNAs can be mistaken for viral RNA by the human/animal immune system, triggering an inflammatory interferon shock via TLR7/8 receptors.
**Implementation Logic:**
1. The engine scans the siRNA for exact Danger-Associated Molecular Patterns (DAMPs).
2. It starts at `0` and adds points cumulatively:
   - **+10 points** per `CG` dinucleotide (mimicking unmethylated viral CpG islands).
   - **+15 points** for exact matches to characterized TLR-activating sequences like `UGUGU` or `GUCCUUCAA`.
   - **+5 points** per GU-rich run (`[GU]{3,}`).
3. The final sum is capped at an output of `100%`.

### D. Overall Enhanced Safety Score
**Output:** Percentage (0-100%)
**Implementation:** This is a mathematically weighted penalization of a perfect score (100).
- `Base = 100`
- `Penalty 1:` -40 if miRNA risk is High, -20 if Medium.
- `Penalty 2:` Subtract `(Complementarity Risk * 0.3)`.
- `Penalty 3:` Subtract `(Immune Score * 0.3)`.
- The final calculation strictly drops below 100 based on exact weights. (e.g. your UI shows 82%).

---

## 2. Module 8: Resistance Evolution Modeling

This forecasting module is handled by `src/lib/analysis/resistanceEvolution.ts`. It predicts how realistically the pest target will evolve a genetic mutation to avoid the pesticide.

### A. Mutation Rate
**Output:** Rate (e.g., `1.37e-6`)
**Implementation Logic:** 
1. The engine parses the precise siRNA string.
2. It separates base opportunities into **Transitions** (A↔G, C↔U) which mutate at a base rate of `1.5e-6` per generation, and **Transversions** (A↔C, G↔U) which mutate at `0.8e-6`.
3. It multiplies these physical probabilities by the Sequence Length (21) to give the exact mathematical likelihood of a random mutation occurring anywhere in the target binding site.

### B. Fitness Cost
**Output:** Percentage (0-100%)
**Background:** If a pest mutates a gene to survive the pesticide, doing so usually inherently damages the gene's function. A 100% Fitness Cost means the mutation itself is lethal.
**Implementation Logic:** 
1. **Base Score:** Uses the Phase 1 *Target Gene Essentiality Score*.
2. **Positional Weighting:** Uses a spatial Trigonometric Sine function (`Math.sin(relativePosition * Math.PI) * 20`) to map the specific target coordinate against the whole gene. Target sites exactly in the dead-center of a gene are functionally penalized harder.
3. The outputs cap at 100%. If you target an essential domain, the pest realistically cannot mutate without killing itself, hence the 100% output.

### C. Escape Mutant Risk
**Output:** `LOW`, `MEDIUM`, or `HIGH`
**Implementation Logic:**
This explicitly multiplies:
`MutationProbability * 1,000,000 * SelectionPressure * (1 - Specificity)`.
If a pest is heavily sprayed (High Pressure), and the site mutation probability is >0.5, Escape Risk is registered as **HIGH**.

### D. Predicted Resistance Time
**Output:** Timeframe (e.g. `<1 year`)
**Implementation Logic:**
1. Estimates Generations Required: `1 / (MutationRate * PopulationSize_Default_10000)`.
2. Adjusts for evolutionary friction using the Fitness Cost: `Generations_To_Resist * (1 + (FitnessCost / 100))`.
3. Assumes an insect life cycle of 10 generations per year. If adjusted generations is <10, it prints `<1 year`.

### E. Overall Durability Score
**Output:** Scaled integer (0-100)
**Implementation Logic:**
Provides the "Shelf-Life" grade of the pesticide.
`Durability = Essentiality_Score - (MutationRate * 1e7) + (FitnessCost * 0.3) - EscapePenalty(30 points)`
A Durability of **58** indicates an unstable pesticide that will face pest evolution rapidly.

---

## 3. Core App Dashboard Stats
*(Total Candidates, Excellent Safety, High Efficiency)*
These outputs are aggregated inside `SiRNADesigner.tsx` using native array filters on the data generated by the algorithms above:
- **Excellent Safety:** `candidates.filter(c => c.safetyScore >= 95).length`
- **High Efficiency:** `candidates.filter(c => c.efficiency >= 85).length`
