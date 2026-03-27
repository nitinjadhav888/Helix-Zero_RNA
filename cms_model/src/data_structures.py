"""
Helix-Zero CMS :: Core Data Structures

Based on research from:
- Martinelli (2024): First ML for chemically modified siRNA
- Liu et al. (2024): Cm-siRPred multi-view learning
- Bramsen et al. (2009): Large-scale modification screen
- Jackson et al. (2006): Position-specific modifications
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum


class ModificationType(Enum):
    """Chemical modification types based on Bramsen et al. (2009)."""

    OME = "2_ome"  # 2'-O-methyl
    FLUORO = "2_f"  # 2'-fluoro
    DNA = "dna"  # 2'-deoxy
    PS = "ps"  # Phosphorothioate
    LNA = "lna"  # Locked Nucleic Acid
    UNA = "una"  # Unlocked Nucleic Acid
    HNA = "hna"  # Hexitol Nucleic Acid
    ANA = "ana"  # Altritol Nucleic Acid


@dataclass
class ModificationProfile:
    """
    Modification impact profile based on Bramsen et al. (2009).

    CALIBRATED VALUES from literature:
    - Bramsen JB et al. (2009) NAR 38:7688 - 2160 siRNA screen
    - Jackson AL et al. (2006) RNA 12:1197 - Position 2 modification
    - Choung S et al. (2006) Biochem Biophys Res Commun 342:919 - 2'-OMe/F optimization
    """

    name: str
    stability_boost_per_nt: float  # hours/nt
    ago2_penalty_per_pyrimidine: float  # %
    ago2_penalty_per_purine: float  # % (typically 2x pyrimidine)
    nuclease_resistance: float  # fraction (0-1)
    immune_suppression: float  # fraction (0-1)
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW

    @classmethod
    def from_type(cls, mod_type: ModificationType) -> "ModificationProfile":
        """Get calibrated profile for modification type."""
        profiles = {
            ModificationType.OME: cls(
                name="2'-O-methyl (2'-OMe)",
                stability_boost_per_nt=0.35,  # Bramsen 2009 Fig 5a (4-8h improvement)
                ago2_penalty_per_pyrimidine=5.0,  # Bramsen 2009 Table 1
                ago2_penalty_per_purine=10.0,  # 2x for purines
                nuclease_resistance=0.85,  # 85% at 24h
                immune_suppression=0.80,  # Choung 2006
                confidence="HIGH",
            ),
            ModificationType.FLUORO: cls(
                name="2'-Fluoro (2'-F)",
                stability_boost_per_nt=0.55,  # Bramsen 2009 (6-12h improvement)
                ago2_penalty_per_pyrimidine=3.0,  # 2'-F is well tolerated
                ago2_penalty_per_purine=6.0,
                nuclease_resistance=0.90,  # 90% at 24h
                immune_suppression=0.85,  # Choung 2006
                confidence="HIGH",
            ),
            ModificationType.PS: cls(
                name="Phosphorothioate (PS)",
                stability_boost_per_nt=0.75,  # Best stability
                ago2_penalty_per_pyrimidine=8.0,  # Higher backbone penalty
                ago2_penalty_per_purine=16.0,
                nuclease_resistance=0.95,  # 95% at 24h
                immune_suppression=0.90,  # Morrissey 2005
                confidence="HIGH",
            ),
            ModificationType.LNA: cls(
                name="Locked Nucleic Acid (LNA)",
                stability_boost_per_nt=1.80,  # Highest stability
                ago2_penalty_per_pyrimidine=35.0,  # High penalty
                ago2_penalty_per_purine=50.0,
                nuclease_resistance=0.95,
                immune_suppression=0.75,
                confidence="HIGH",
            ),
            ModificationType.UNA: cls(
                name="Unlocked Nucleic Acid (UNA)",
                stability_boost_per_nt=-0.10,  # Destabilizing
                ago2_penalty_per_pyrimidine=-5.0,  # Negative = helps strand separation
                ago2_penalty_per_purine=-8.0,
                nuclease_resistance=0.30,
                immune_suppression=0.20,
                confidence="MEDIUM",
            ),
        }
        return profiles.get(mod_type, profiles[ModificationType.OME])


@dataclass
class siRNAsequence:
    """
    siRNA sequence representation.

    Attributes:
        sequence: Raw nucleotide sequence (A, U, G, C)
        length: Number of nucleotides (typically 21)
        modifications: List of (position, mod_type) tuples
    """

    sequence: str
    modifications: List[Tuple[int, ModificationType]] = field(default_factory=list)

    def __post_init__(self):
        self.sequence = self.sequence.upper()
        self.length = len(self.sequence)

        valid_bases = set("AUCG")
        if not all(base in valid_bases for base in self.sequence):
            raise ValueError(
                f"Invalid sequence. Bases must be A, U, C, or G. Got: {self.sequence}"
            )

        if self.length not in [19, 20, 21]:
            raise ValueError(f"Invalid length {self.length}. Must be 19, 20, or 21.")

    @property
    def gc_content(self) -> float:
        """Calculate GC content percentage."""
        gc = sum(1 for b in self.sequence if b in "GC")
        return (gc / self.length) * 100

    @property
    def positions(self) -> List[int]:
        """Get list of positions."""
        return list(range(self.length))

    def get_modifications_at(self, position: int) -> List[ModificationType]:
        """Get all modifications at a specific position."""
        return [mod for pos, mod in self.modifications if pos == position]

    def is_modified(self, position: int) -> bool:
        """Check if position has any modification."""
        return any(pos == position for pos, _ in self.modifications)

    def get_base(self, position: int) -> str:
        """Get base at position."""
        return self.sequence[position]


@dataclass
class PredictionResult:
    """
    Result of CMS prediction.

    Based on Therapeutic Index formula from Helix-Zero V7.
    """

    original_sequence: str
    modified_sequence: str
    modification_type: str
    positions_modified: List[int]

    # Core metrics
    half_life_hours: float
    ago2_binding_percent: float
    immune_suppression_percent: float
    therapeutic_index: float

    # Detailed metrics
    pyrimidine_modifications: int
    purine_modifications: int
    cleavage_zone_violations: int

    # Assessment
    recommendation: str
    efficacy_category: str

    @property
    def stability_score(self) -> float:
        """Calculate stability score (0-100)."""
        return min(self.half_life_hours / 72 * 100, 100)

    @property
    def activity_score(self) -> float:
        """Calculate activity score (0-100)."""
        return self.ago2_binding_percent

    @classmethod
    def from_calculation(
        cls, sequence: siRNAsequence, mod_type: ModificationType, positions: List[int]
    ) -> "PredictionResult":
        """Create result from calculation."""
        from src.calculations import (
            calculate_half_life,
            calculate_ago2_binding,
            calculate_immune_suppression,
            calculate_therapeutic_index,
            get_recommendation,
            classify_efficacy,
            count_cleavage_violations,
            count_pyrimidine_mods,
        )

        profile = ModificationProfile.from_type(mod_type)

        half_life = calculate_half_life(sequence, positions, profile)
        ago2 = calculate_ago2_binding(sequence, positions, profile)
        immune = calculate_immune_suppression(sequence, positions, profile)
        ti = calculate_therapeutic_index(half_life, ago2)

        violations = count_cleavage_violations(positions)
        pyrimidine_count = count_pyrimidine_mods(sequence, positions)
        purine_count = len(positions) - pyrimidine_count

        modified_seq = list(sequence.sequence)
        for p in positions:
            if 0 <= p < len(modified_seq):
                modified_seq[p] = f"[{modified_seq[p]}*]"

        recommendation = get_recommendation(ti, ago2, half_life)
        category = classify_efficacy(ti)

        return cls(
            original_sequence=sequence.sequence,
            modified_sequence="".join(modified_seq),
            modification_type=profile.name,
            positions_modified=positions,
            half_life_hours=half_life,
            ago2_binding_percent=ago2,
            immune_suppression_percent=immune,
            therapeutic_index=ti,
            pyrimidine_modifications=pyrimidine_count,
            purine_modifications=purine_count,
            cleavage_zone_violations=violations,
            recommendation=recommendation,
            efficacy_category=category,
        )
