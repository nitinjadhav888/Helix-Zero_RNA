"""
Helix-Zero V8 :: 3D RNA Target Accessibility Engine
Nearest-Neighbor Thermodynamic Proxy for RNA secondary structure analysis.

This provides a pure-Python approximation of the energy required to "un-knot"
the target mRNA region so the RISC complex can bind. No external C-library
(ViennaRNA) is required.

Theory:
  An siRNA can only silence its target if the RISC complex can physically
  access that region of the mRNA. If the target site is buried in a tight
  thermodynamic "knot" (a hairpin, internal loop, or long duplex), RISC
  cannot enter, and the siRNA fails in vivo even if it is perfectly designed.

  We approximate accessibility as:
    ΔG_net = ΔG_binding − ΔG_unfolding

  If ΔG_net < −10 kcal/mol → Site is highly accessible (RISC wins)
  If ΔG_net > 0 kcal/mol  → Site is blocked (RISC cannot enter)

References:
  - Mathews et al. (1999) Nearest-neighbor parameters for RNA thermodynamics
  - Free et al. (2015) mRNA target site accessibility in siRNA design
"""

# ── Nearest-Neighbor ΔG Lookup Table (RNA, 37°C, kcal/mol) ──────────────────
# fmt: off
# Stacking energies for RNA duplex: {5'-XY-3' / 3'-WZ-5'}
# Data from SantaLucia (1998) and Mathews (1999) adapted for RNA
_NN_PARAMS = {
    "AA": -0.93, "AU": -1.10, "AC": -2.11, "AG": -2.24,
    "UA": -1.33, "UU": -0.93, "UC": -2.08, "UG": -2.11,
    "CA": -2.11, "CU": -1.33, "CC": -3.26, "CG": -2.36,
    "GA": -2.35, "GU": -2.35, "GC": -3.42, "GG": -3.26,
}
# Penalty for non-Watson-Crick base wobble pairs (G:U) and mismatches
_WOBBLE_BONUS  = +0.50   # G:U wobbles reduce stability slightly  (kcal/mol)
_MISMATCH_PENALTY = +3.50   # Non-paired bases add destabilisation   (kcal/mol)

# fmt: on

_RNA_COMPLEMENT = str.maketrans("ATCG", "UAGC")
_DNA_TO_RNA     = str.maketrans("T", "U")


def _to_rna(seq: str) -> str:
    return seq.upper().translate(_DNA_TO_RNA)


def _calc_duplex_dg(sense: str, antisense: str) -> float:
    """
    Calculate duplex ΔG between two RNA strands using Nearest-Neighbor parameters.
    Positive value → less stable (easier to melt = more accessible).
    """
    dg = 0.0
    s  = _to_rna(sense)
    a  = _to_rna(antisense)

    length = min(len(s), len(a))
    for i in range(length - 1):
        dinuc = s[i:i+2]
        dg += _NN_PARAMS.get(dinuc, -1.5)  # default to moderate stability

    # Initiation penalty (every duplex pays a ~4 kcal/mol penalty to start)
    dg += 4.09

    return round(dg, 2)


def _estimate_target_folding_dg(target_region: str) -> float:
    """
    Estimate the free energy cost of UN-FOLDING the target mRNA region.

    A higher (more positive) value means the site is MORE buried in structure,
    making it HARDER to access.

    We approximate by checking for self-complementarity within the window:
    runs of G/C pairs create stable hairpins, while AU-rich regions are
    naturally open/accessible.
    """
    seq = _to_rna(target_region)
    length = len(seq)
    
    gc_content = (seq.count("G") + seq.count("C")) / length * 100
    
    # GC-rich regions form tighter secondary structures (harder to melt)
    gc_penalty = (gc_content - 40.0) / 100.0 * 8.0  # kcal/mol scaled
    
    # Long runs of G (G-quadruplexes) or C (polycytidine) are very stable
    g_run_penalty = 0.0
    for run_len in range(6, 3, -1):
        if "G" * run_len in seq or "C" * run_len in seq:
            g_run_penalty = run_len * 1.2
            break
    
    # Self-complementarity scan (crude palindrome detection → hairpin energy)
    hairpin_penalty = 0.0
    complement = {"A": "U", "U": "A", "G": "C", "C": "G"}
    for win_size in range(8, 4, -1):
        for start in range(length - win_size + 1):
            sub = seq[start:start + win_size]
            rev_comp = "".join(complement.get(c, c) for c in reversed(sub))
            if sub == rev_comp:
                hairpin_penalty = win_size * 0.8
                break
        if hairpin_penalty > 0:
            break
    
    # Unfolding cost = structural penalty − natural AU-loop openness
    au_openness = (seq.count("A") + seq.count("U")) / length * 3.0
    unfolding_dg = gc_penalty + g_run_penalty + hairpin_penalty - au_openness
    
    return round(unfolding_dg, 2)


def calculate_accessibility(candidate_seq: str, target_context: str = None) -> dict:
    """
    Main API function: Calculate the thermodynamic accessibility of an mRNA target site.

    Args:
        candidate_seq:   The 21-nt siRNA candidate sequence
        target_context:  Optional flanking context of the mRNA (up to 50nt).
                         If None, the candidate itself is used as its own target context.

    Returns:
        dict with:
          - dg_binding       : ΔG of siRNA:mRNA duplex formation (kcal/mol)
          - dg_unfolding     : ΔG cost to open the target site (kcal/mol)
          - dg_net           : Net binding energy (binding - unfolding)
          - accessibilityScore: 0-100 score (100 = perfectly accessible)
          - accessibilityClass: "Open", "Moderate", "Restricted", "Blocked"
          - interpretation   : Human-readable assessment
    """
    seq = _to_rna(candidate_seq.upper())
    context = _to_rna((target_context or candidate_seq).upper())
    
    # Compute the complement of the siRNA (this pairs with target mRNA)
    complement_map = {"A": "U", "U": "A", "G": "C", "C": "G"}
    guide_antisense = "".join(complement_map.get(c, c) for c in reversed(seq))
    
    # ΔG of siRNA binding to the target mRNA (should be very negative = good)
    dg_binding = _calc_duplex_dg(seq, guide_antisense)
    
    # ΔG cost to unfold the target mRNA region (site must be opened first)
    dg_unfolding = _estimate_target_folding_dg(context[:len(seq)])
    
    # Net thermodynamic favourability
    dg_net = round(dg_binding - dg_unfolding, 2)
    
    # Convert to 0-100 accessibility score
    # dg_net < -15 → 100 (super accessible), dg_net > 0 → 0 (blocked)
    if dg_net < -20:
        acc_score = 100.0
    elif dg_net < -15:
        acc_score = 90.0 + ((-15 - dg_net) / 5.0) * 10.0
    elif dg_net < -10:
        acc_score = 70.0 + ((-10 - dg_net) / 5.0) * 20.0
    elif dg_net < -5:
        acc_score = 45.0 + ((-5 - dg_net) / 5.0) * 25.0
    elif dg_net < 0:
        acc_score = 20.0 + ((-dg_net) / 5.0) * 25.0
    else:
        acc_score = max(0.0, 20.0 - dg_net * 5.0)
    
    acc_score = round(min(100.0, max(0.0, acc_score)), 1)
    
    # Classification
    if acc_score >= 80:
        acc_class = "Open"
        interp = f"Target site is highly accessible (ΔG_net={dg_net}). RISC loading is thermodynamically favoured."
    elif acc_score >= 55:
        acc_class = "Moderate"
        interp = f"Target site has moderate structure (ΔG_net={dg_net}). RISC should still bind with normal efficiency."
    elif acc_score >= 30:
        acc_class = "Restricted"
        interp = f"Target site is partially structured (ΔG_net={dg_net}). RISC loading may be impaired. Consider alternative sites."
    else:
        acc_class = "Blocked"
        interp = f"Target site is deeply buried in mRNA structure (ΔG_net={dg_net}). RISC cannot enter. Avoid this site."
    
    return {
        "dgBinding":          dg_binding,
        "dgUnfolding":        dg_unfolding,
        "dgNet":              dg_net,
        "accessibilityScore": acc_score,
        "accessibilityClass": acc_class,
        "interpretation":     interp,
    }
