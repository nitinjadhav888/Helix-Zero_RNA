"""
Helix-Zero CMS :: Thermodynamic Calculations

Based on:
- SantaLucia (1998): Nearest-neighbor thermodynamics
- Mathews et al. (2004): RNA structure with chemical modification constraints
- Turner & Mathews (2010): Expanded nearest-neighbor parameters
"""

import math
from typing import Dict, Tuple, List
from src.data_structures import siRNAsequence, ModificationProfile, ModificationType


# ═══════════════════════════════════════════════════════════════════════════
# NEAREST-NEIGHBOR PARAMETERS (SantaLucia 1998)
# ═══════════════════════════════════════════════════════════════════════════

NN_PARAMS: Dict[str, Tuple[float, float]] = {
    # Dinucleotide: (ΔH° in kcal/mol, ΔS° in cal/mol·K)
    "AA": (-7.9, -22.2),
    "UU": (-7.9, -22.2),
    "AT": (-7.2, -20.4),
    "TA": (-7.2, -21.3),
    "AU": (-7.2, -20.4),
    "UA": (-7.2, -21.3),
    "AC": (-8.4, -22.4),
    "GT": (-8.4, -22.4),
    "CA": (-8.5, -22.7),
    "AG": (-7.8, -21.0),
    "CT": (-7.8, -21.0),
    "GA": (-8.2, -22.2),
    "CG": (-10.6, -27.2),
    "GC": (-9.8, -24.4),
    "GG": (-8.0, -19.9),
    "CC": (-8.0, -19.9),
    "GU": (-8.4, -22.4),  # Wobble pair
    "UG": (-8.5, -22.7),  # Wobble pair
}


def calculate_mfe(seq: str, temperature: float = 37.0) -> float:
    """
    Calculate Minimum Free Energy using Nearest-Neighbor thermodynamics.
    
    Formula: ΔG°37 = ΔH° - T × ΔS°
    
    Args:
        seq: RNA sequence
        temperature: Temperature in Celsius (default 37°C)
    
    Returns:
        MFE in kcal/mol
    
    Reference: SantaLucia (1998) PNAS 95:1460-1465
    """
    T = temperature + 273.15  # Convert to Kelvin
    
    total_dh = 0.0  # Enthalpy (kcal/mol)
    total_ds = 0.0  # Entropy (cal/mol·K)
    
    for i in range(len(seq) - 1):
        dinuc = seq[i:i+2]
        if dinuc in NN_PARAMS:
            dh, ds = NN_PARAMS[dinuc]
            total_dh += dh
            total_ds += ds
    
    # Convert entropy to kcal/mol·K
    mfe = total_dh - T * (total_ds / 1000.0)
    
    return round(mfe, 2)


def calculate_melting_temperature(seq: str) -> float:
    """
    Calculate melting temperature (Tm) for short oligonucleotides.
    
    Uses nearest-neighbor method.
    
    Formula: Tm = ΔH° / (ΔS° + R × ln(Ct/4)) - 273.15
    
    Where:
        R = 1.987 cal/mol·K (gas constant)
        Ct = initial concentration (assume 250 nM)
    
    Reference: SantaLucia & Turner (1997)
    """
    R = 1.987  # Gas constant in cal/mol·K
    Ct = 250e-9  # 250 nM in M
    
    total_dh = 0.0
    total_ds = 0.0
    
    for i in range(len(seq) - 1):
        dinuc = seq[i:i+2]
        if dinuc in NN_PARAMS:
            dh, ds = NN_PARAMS[dinuc]
            total_dh += dh
            total_ds += ds
    
    # Add initiation parameters
    if seq[0] in "GC":
        total_dh += 0.1
    else:
        total_dh += 2.3
    
    if seq[-1] in "GC":
        total_dh += 0.1
    else:
        total_dh += 2.3
    
    # Calculate Tm
    tm_kelvin = total_dh / (total_ds + R * math.log(Ct / 4))
    tm_celsius = tm_kelvin - 273.15
    
    return round(tm_celsius, 2)


def calculate_thermodynamic_asymmetry(seq: str) -> float:
    """
    Calculate 5' vs 3' thermodynamic asymmetry.
    
    Positive value = 5' end is thermodynamically weaker
    This is desirable for RISC loading (guide strand selection).
    
    Reference: Khvorova et al. (2003) Cell 115:209-216
    """
    # Calculate energy of first 4 nucleotides (5' end)
    end_5_prime = seq[:4]
    energy_5 = calculate_mfe(end_5_prime) if len(end_5_prime) >= 2 else 0
    
    # Calculate energy of last 4 nucleotides (3' end)
    end_3_prime = seq[-4:]
    energy_3 = calculate_mfe(end_3_prime) if len(end_3_prime) >= 2 else 0
    
    asymmetry = energy_3 - energy_5
    
    return round(asymmetry, 2)


# ═══════════════════════════════════════════════════════════════════════════
# HELIX-ZERO CMS CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════

# Critical positions based on Jackson et al. (2006) and Bramsen et al. (2009)
CLEAVAGE_ZONE = set(range(9, 13))  # Positions 9-12 (0-indexed)
SEED_REGION = set(range(1, 8))  # Positions 2-8 (0-indexed: 1-7)


def calculate_half_life(
    sequence: siRNAsequence,
    positions: List[int],
    profile: ModificationProfile
) -> float:
    """
    Calculate stability half-life based on modifications.
    
    Formula:
        HalfLife = (0.5 × Nuclease_Factor) + Stability_Boost
    
    Where:
        Nuclease_Factor = 1.0 - (num_modified/length) × (1 - nuclease_resistance)
        Stability_Boost = (pyrimidines × 1.5 + purines × 0.5) × boost_per_nt
    
    Reference: Bramsen et al. (2009) NAR 38:7688
    """
    length = sequence.length
    num_modified = len(positions)
    
    # Calculate nuclease factor
    nuclease_factor = 1.0 - (num_modified / length) * (1 - profile.nuclease_resistance)
    
    # Count pyrimidine vs purine modifications
    pyrimidine_count = sum(
        1 for pos in positions 
        if sequence.get_base(pos) in 'UC'
    )
    purine_count = num_modified - pyrimidine_count
    
    # Calculate stability boost
    stability_boost = (
        pyrimidine_count * 1.5 + 
        purine_count * 0.5
    ) * profile.stability_boost_per_nt
    
    # Calculate half-life
    half_life = (0.5 * nuclease_factor) + stability_boost
    
    return round(half_life, 2)


def calculate_ago2_binding(
    sequence: siRNAsequence,
    positions: List[int],
    profile: ModificationProfile
) -> float:
    """
    Calculate Ago2 binding affinity based on modifications.
    
    Formula:
        Ago2_Binding = 100% - Ago2_Penalty
    
    Where:
        Ago2_Penalty = (purines × 2.0 + pyrimidines × 1.0) × penalty_per_nt 
                     + cleavage_violations × 25.0
    
    Critical Rule: Positions 9-12 (cleavage zone) must NOT be modified
                  because Ago2 requires 2'-OH for catalytic cleavage.
    
    Reference: Jackson et al. (2006) RNA 12:1197-1205
    Reference: Bramsen et al. (2009) NAR 38:7688
    """
    pyrimidine_count = sum(
        1 for pos in positions 
        if sequence.get_base(pos) in 'UC'
    )
    purine_count = len(positions) - pyrimidine_count
    
    # Calculate penalty per nucleotide type
    pyrimidine_penalty = pyrimidine_count * profile.ago2_penalty_per_pyrimidine
    purine_penalty = purine_count * profile.ago2_penalty_per_purine
    
    # Calculate cleavage zone violations
    cleavage_violations = sum(1 for pos in positions if pos in CLEAVAGE_ZONE)
    
    # Total penalty
    total_penalty = pyrimidine_penalty + purine_penalty + (cleavage_violations * 25.0)
    
    # Ago2 binding
    ago2_binding = max(0, 100 - total_penalty)
    
    return round(ago2_binding, 2)


def calculate_immune_suppression(
    sequence: siRNAsequence,
    positions: List[int],
    profile: ModificationProfile
) -> float:
    """
    Calculate immune response suppression (TLR activation reduction).
    
    Formula:
        Immune_Suppression = immune_factor × (modified/length) × 100
    
    Chemical modifications reduce TLR (Toll-like Receptor) activation,
    which triggers innate immune responses.
    
    Reference: Robbins et al. (2009) Nat Biotechnol 27:478-480
    """
    length = sequence.length
    num_modified = len(positions)
    
    immune_suppression = profile.immune_suppression * (num_modified / length) * 100
    
    return round(immune_suppression, 2)


def calculate_therapeutic_index(half_life: float, ago2_binding: float) -> float:
    """
    Calculate Therapeutic Index (primary optimization target).
    
    Formula:
        Therapeutic_Index = (HalfLife_Score × 0.5) + (Ago2_Score × 0.5)
    
    Where:
        HalfLife_Score = min(HalfLife / 72, 1.0) × 100
        Ago2_Score = Ago2_Binding
    
    The therapeutic index balances:
    1. Stability (longer half-life in vivo)
    2. Activity (maintained RISC loading and cleavage)
    
    Reference: Helix-Zero V7 Design
    """
    half_life_score = min(half_life / 72, 1.0) * 100
    
    therapeutic_index = (half_life_score * 0.5) + (ago2_binding * 0.5)
    
    return round(therapeutic_index, 2)


def get_recommendation(ti: float, ago2: float, half_life: float) -> str:
    """
    Generate recommendation based on metrics.
    
    Based on clinical thresholds from FDA-approved siRNA drugs.
    """
    if ti >= 70 and ago2 >= 80:
        return "Excellent candidate for in vivo application. High stability with maintained activity."
    elif ti >= 50 and ago2 >= 60:
        return "Good candidate. Consider further optimization of modification positions."
    elif ti >= 30:
        return "Moderate candidate. Review modification positions and consider alternative types."
    else:
        return "Poor candidate. Cleavage zone violation or excessive activity loss. Redesign recommended."


def classify_efficacy(ti: float) -> str:
    """
    Classify efficacy category based on Therapeutic Index.
    
    Categories based on Cm-siRPred thresholds (Liu et al. 2024).
    """
    if ti >= 70:
        return "Excellent"
    elif ti >= 50:
        return "Good"
    elif ti >= 30:
        return "Moderate"
    else:
        return "Poor"


def apply_modifications(sequence: siRNAsequence, positions: List[int]) -> str:
    """Format sequence string with modifications shown by lowercase."""
    seq_list = list(sequence.sequence)
    for pos in positions:
        if 0 <= pos < len(seq_list):
            seq_list[pos] = seq_list[pos].lower()
    return "".join(seq_list)


def count_cleavage_violations(positions: List[int]) -> int:
    """Count modifications in cleavage zone (positions 9-12)."""
    return sum(1 for pos in positions if pos in CLEAVAGE_ZONE)


def count_pyrimidine_mods(sequence: siRNAsequence, positions: List[int]) -> int:
    """Count number of modified pyrimidines (U, C)."""
    return sum(1 for pos in positions if sequence.get_base(pos) in 'UC')