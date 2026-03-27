"""
Helix-Zero V8 :: RNA Secondary Structure Prediction Engine
Nussinov Algorithm for 2D RNA Structure Prediction

This module provides true 2D structure prediction for RNA molecules,
showing base-pairing patterns, hairpins, loops, and bulges.

Theory:
  RNA molecules fold into specific secondary structures based on Watson-Crick
  and Wobble base pairing. The Nussinov algorithm finds the optimal folding
  by maximizing the number of base pairs.

Base Pairing Rules:
  - A-U (2 hydrogen bonds)
  - G-C (3 hydrogen bonds)
  - G-U Wobble (2 hydrogen bonds, less stable)

Structure Elements:
  - Hairpin Loop: Unpaired nucleotides that form the loop of a hairpin
  - Internal Loop: Gap in base pairing on both strands
  - Bulge: Gap in base pairing on one strand only
  - Stem: The stacked base pairs forming the stem of a hairpin
  - Multi-loop: Junction of three or more stems

References:
  - Nussinov & Jacobson (1980) Algorithm for finding base pairing maximum
  - Mathews et al. (1999) RNA secondary structure prediction
  - Turner & Mathews (2010) Nearest-neighbor parameters
"""

import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

# ── Base Pairing Energy Parameters (kcal/mol) ──────────────────────────────────
# Negative = favorable (stable)
BASE_PAIR_ENERGY = {
    "GC": -3.0,  # Strongest: 3 H-bonds
    "CG": -3.0,
    "AU": -2.0,  # Moderate: 2 H-bonds
    "UA": -2.0,
    "GU": -1.0,  # Wobble pair: 2 H-bonds, less stable
    "UG": -1.0,
}

# Allowed base pairs
VALID_PAIRS = {"GC", "CG", "AU", "UA", "GU", "UG"}


@dataclass
class BasePair:
    """Represents a base pair in the RNA structure."""

    pos5: int  # 5' position (0-indexed)
    pos3: int  # 3' position (0-indexed)
    pair_type: str  # "GC", "AU", "GU"
    energy: float  # Free energy contribution


@dataclass
class StructureElement:
    """Represents a structural element in the RNA."""

    element_type: str  # "hairpin", "internal_loop", "bulge", "stem", "multiloop"
    start: int
    end: int
    length: int
    description: str


class NussinovSolver:
    """
    Nussinov Algorithm for RNA Secondary Structure Prediction.

    This algorithm finds the optimal folding by dynamic programming,
    maximizing the number of base pairs while respecting biological constraints.

    Constraints:
    - No pseudoknots (structures cannot cross)
    - Minimum hairpin loop size: 3 nucleotides
    - Only canonical base pairs allowed (GC, AU, GU)
    """

    def __init__(self, min_loop_size: int = 3):
        self.min_loop_size = min_loop_size
        self.sequence = ""
        self.n = 0
        self.dp = None  # Dynamic programming table
        self.traceback = None  # For reconstructing structure
        self.base_pairs = []
        self.dot_bracket = ""

    def predict(self, sequence: str) -> Dict:
        """
        Predict the secondary structure of an RNA sequence.

        Args:
            sequence: RNA sequence (A, U, G, C)

        Returns:
            Dictionary containing structure prediction results
        """
        # Preprocess sequence
        self.sequence = sequence.upper().replace("T", "U")
        self.n = len(self.sequence)

        if self.n < 6:
            return {
                "sequence": self.sequence,
                "dot_bracket": "." * self.n,
                "structure_score": 0,
                "num_base_pairs": 0,
                "base_pairs": [],
                "elements": [],
                "accessibility_prediction": "Too short to analyze",
                "visual": self.sequence,
            }

        # Initialize DP table
        self.dp = [[0.0 for _ in range(self.n)] for _ in range(self.n)]
        self.traceback = [[None for _ in range(self.n)] for _ in range(self.n)]

        # Fill DP table
        self._fill_dp_table()

        # Traceback to find base pairs
        self._traceback()

        # Generate dot-bracket notation
        self.dot_bracket = self._generate_dot_bracket()

        # Identify structural elements
        elements = self._identify_elements()

        # Calculate structure score
        structure_score = self._calculate_structure_score()

        # Predict accessibility
        accessibility = self._predict_accessibility()

        # Generate ASCII visualization
        visual = self._generate_visualization()

        return {
            "sequence": self.sequence,
            "length": self.n,
            "dot_bracket": self.dot_bracket,
            "structure_score": structure_score,
            "num_base_pairs": len(self.base_pairs),
            "base_pairs": [
                (bp.pos5, bp.pos5 + 1, bp.pos3 + 1, bp.pair_type, bp.energy)
                for bp in self.base_pairs
            ],
            "elements": elements,
            "accessibility_prediction": accessibility,
            "visual": visual,
            "gc_content": self._calculate_gc_content(),
            "mfe_estimate": self._estimate_mfe(),
        }

    def _fill_dp_table(self):
        """Fill the dynamic programming table using Nussinov recurrence."""
        # Fill for increasing sequence lengths
        for length in range(2, self.n + 1):
            for i in range(self.n - length + 1):
                j = i + length - 1

                # Case 1: j is unpaired
                self.dp[i][j] = self.dp[i][j - 1]
                self.traceback[i][j] = ("unpaired", i, j - 1)

                # Case 2: j pairs with some k (i <= k < j)
                for k in range(i, j - self.min_loop_size):
                    if self._can_pair(k, j):
                        # Pair k with j, plus optimal structure for i to k-1 and k+1 to j-1
                        score = 1 + self.dp[i][k - 1] if k > i else 1
                        if k + 1 <= j - 1:
                            score += self.dp[k + 1][j - 1]

                        if score > self.dp[i][j]:
                            self.dp[i][j] = score
                            self.traceback[i][j] = ("pair", k, j)

    def _can_pair(self, i: int, j: int) -> bool:
        """Check if positions i and j can form a base pair."""
        if j - i < self.min_loop_size:
            return False
        pair = self.sequence[i] + self.sequence[j]
        return pair in VALID_PAIRS

    def _traceback(self):
        """Traceback through DP table to find base pairs."""
        self.base_pairs = []
        self._traceback_recursive(0, self.n - 1)
        self.base_pairs.sort(key=lambda x: x.pos5)

    def _traceback_recursive(self, i: int, j: int):
        """Recursive traceback."""
        if i >= j:
            return

        action = self.traceback[i][j]
        if action is None:
            return

        action_type = action[0]

        if action_type == "unpaired":
            self._traceback_recursive(i, j - 1)
        elif action_type == "pair":
            k = action[1]
            pair = self.sequence[k] + self.sequence[j]
            energy = BASE_PAIR_ENERGY.get(pair, -1.0)
            self.base_pairs.append(BasePair(k, j, pair, energy))

            # Traceback left side
            if k > i:
                self._traceback_recursive(i, k - 1)

            # Traceback right side (between k+1 and j-1)
            if k + 1 <= j - 1:
                self._traceback_recursive(k + 1, j - 1)

    def _generate_dot_bracket(self) -> str:
        """Generate dot-bracket notation from base pairs."""
        dot_bracket = ["."] * self.n
        pair_map = {}

        for bp in self.base_pairs:
            pair_map[bp.pos5] = bp.pos3
            pair_map[bp.pos3] = bp.pos5

        # Simple approach: find matching pairs
        for bp in self.base_pairs:
            i, j = bp.pos5, bp.pos3
            # Find the next available opening bracket
            opening_count = sum(1 for bp2 in self.base_pairs if bp2.pos5 < i)
            closing_count = sum(
                1 for bp2 in self.base_pairs if bp2.pos3 > j and bp2.pos5 > i
            )

            # Use simple bracket assignment
            if i < j:
                dot_bracket[i] = "("
                dot_bracket[j] = ")"

        return "".join(dot_bracket)

    def _identify_elements(self) -> List[Dict]:
        """Identify structural elements from base pairs."""
        elements = []

        if not self.base_pairs:
            elements.append(
                {
                    "type": "single_stranded",
                    "start": 0,
                    "end": self.n - 1,
                    "length": self.n,
                    "description": "No base pairs - unstructured region",
                }
            )
            return elements

        # Sort base pairs by position
        sorted_pairs = sorted(self.base_pairs, key=lambda x: x.pos5)

        # Find hairpins and stems
        i = 0
        while i < len(sorted_pairs):
            bp = sorted_pairs[i]

            # Check for hairpin
            next_i = i + 1
            if next_i < len(sorted_pairs):
                next_bp = sorted_pairs[next_i]
                if next_bp.pos5 - bp.pos5 > 1:
                    # Hairpin loop detected
                    loop_start = bp.pos5 + 1
                    loop_end = next_bp.pos5 - 1
                    if loop_start <= loop_end:
                        elements.append(
                            {
                                "type": "hairpin_loop",
                                "start": loop_start,
                                "end": loop_end,
                                "length": loop_end - loop_start + 1,
                                "stem_5prime": bp.pos5,
                                "stem_3prime": bp.pos3,
                                "description": f"Hairpin loop ({loop_end - loop_start + 1} nt)",
                            }
                        )

            # Stem segment
            stem_length = 1
            j = i
            while j + 1 < len(sorted_pairs):
                next_bp = sorted_pairs[j + 1]
                # Check if consecutive (adjacent in stem)
                if (
                    next_bp.pos5 == sorted_pairs[j].pos5 + 1
                    and next_bp.pos3 == sorted_pairs[j].pos3 - 1
                ):
                    stem_length += 1
                    j += 1
                else:
                    break

            if stem_length >= 2:
                elements.append(
                    {
                        "type": "stem",
                        "start": sorted_pairs[i].pos5,
                        "end": sorted_pairs[j].pos5 + 1,
                        "length": stem_length,
                        "bp_5prime": [bp.pos5 for bp in sorted_pairs[i : j + 1]],
                        "bp_3prime": [bp.pos3 for bp in sorted_pairs[i : j + 1]],
                        "description": f"Stem helix ({stem_length} base pairs)",
                    }
                )

            i = max(i + 1, j + 1)

        # Find terminal regions
        if sorted_pairs:
            first_bp = sorted_pairs[0]
            last_bp = sorted_pairs[-1]

            if first_bp.pos5 > 0:
                elements.append(
                    {
                        "type": "overhang_5prime",
                        "start": 0,
                        "end": first_bp.pos5 - 1,
                        "length": first_bp.pos5,
                        "description": "5' overhang (unpaired)",
                    }
                )

            if last_bp.pos3 < self.n - 1:
                elements.append(
                    {
                        "type": "overhang_3prime",
                        "start": last_bp.pos3 + 1,
                        "end": self.n - 1,
                        "length": self.n - last_bp.pos3 - 1,
                        "description": "3' overhang (unpaired)",
                    }
                )

        return elements

    def _calculate_structure_score(self) -> float:
        """
        Calculate structure stability score based on:
        - Number of base pairs
        - Energy of base pairs
        - Loop penalties
        """
        if not self.base_pairs:
            return 0.0

        # Total base pair energy
        total_energy = sum(bp.energy for bp in self.base_pairs)

        # Normalize by sequence length
        score = -total_energy / self.n * 100  # Negative energy is favorable

        return round(max(0, min(100, score)), 1)

    def _predict_accessibility(self) -> Dict:
        """
        Predict RNA accessibility based on structure.
        More base pairs = less accessible for siRNA binding.
        """
        if not self.base_pairs:
            return {
                "classification": "Fully Accessible",
                "score": 100,
                "reason": "No secondary structure detected - fully open for RISC binding",
            }

        accessibility_score = 100 - (len(self.base_pairs) / self.n * 100)

        if accessibility_score >= 80:
            classification = "Highly Accessible"
            reason = "Minimal secondary structure - RISC can easily bind"
        elif accessibility_score >= 60:
            classification = "Moderately Accessible"
            reason = (
                "Some structure present but should not significantly impede binding"
            )
        elif accessibility_score >= 40:
            classification = "Partially Restricted"
            reason = "Significant structure may slow RISC binding"
        else:
            classification = "Restricted"
            reason = "Strong secondary structure may block RISC binding"

        return {
            "classification": classification,
            "score": round(accessibility_score, 1),
            "reason": reason,
            "num_base_pairs": len(self.base_pairs),
            "base_pair_density": round(len(self.base_pairs) / self.n * 100, 1),
        }

    def _calculate_gc_content(self) -> float:
        """Calculate GC content of the sequence."""
        gc = sum(1 for c in self.sequence if c in "GC")
        return round(gc / self.n * 100, 1) if self.n > 0 else 0

    def _estimate_mfe(self) -> float:
        """Estimate minimum free energy based on base pairs."""
        if not self.base_pairs:
            return 0.0
        return round(sum(bp.energy for bp in self.base_pairs), 2)

    def _generate_visualization(self) -> str:
        """Generate ASCII visualization of the RNA structure."""
        if not self.base_pairs:
            return f"5'-{self.sequence}-3'\n(No predicted structure)"

        lines = []

        # Create pair mapping
        pair_map = {}
        for bp in self.base_pairs:
            pair_map[bp.pos5] = bp.pos3
            pair_map[bp.pos3] = bp.pos5

        # Line 1: Sequence with positions
        seq_line = "5'-"
        for i, c in enumerate(self.sequence):
            seq_line += c
        seq_line += "-3'"
        lines.append(seq_line)

        # Line 2: Vertical connectors for base pairs
        connector = [" "] * (self.n + 4)
        for bp in self.base_pairs:
            i, j = bp.pos5, bp.pos3
            # Find columns
            col_i = 3 + i
            col_j = 3 + j
            if col_i < len(connector) and col_j < len(connector):
                connector[col_i] = "|"
                connector[col_j] = "|"
        lines.append("    " + "".join(connector[: self.n]))

        # Line 3: Sequence on opposite strand
        rev_seq = self.sequence[::-1]
        opp_line = "3'-"
        for i, c in enumerate(rev_seq):
            opp_line += c
        opp_line += "-5'"
        lines.append(opp_line)

        # Add dot-bracket
        lines.append(f"\nDot-Bracket: {self.dot_bracket}")

        # Add element legend
        elements = self._identify_elements()
        element_types = [e["type"] for e in elements]
        lines.append(f"\nStructure Elements: {', '.join(set(element_types))}")

        return "\n".join(lines)


def predict_rna_structure(sequence: str) -> Dict:
    """
    Main API function for RNA secondary structure prediction.

    Args:
        sequence: RNA or DNA sequence (will convert T to U)

    Returns:
        Dictionary containing:
        - sequence: Cleaned RNA sequence
        - length: Sequence length
        - dot_bracket: Structure in dot-bracket notation
        - structure_score: Stability score (0-100)
        - num_base_pairs: Number of predicted base pairs
        - base_pairs: List of base pairs with positions
        - elements: List of structural elements
        - accessibility_prediction: Accessibility analysis
        - visual: ASCII visualization
        - gc_content: GC percentage
        - mfe_estimate: Estimated minimum free energy
    """
    solver = NussinovSolver(min_loop_size=3)
    return solver.predict(sequence)


def compare_sites(sequences: List[str], site_positions: List[int] = None) -> Dict:
    """
    Compare RNA structure accessibility across multiple target sites.
    Useful for selecting the most accessible siRNA target site.

    Args:
        sequences: List of RNA sequences to compare
        site_positions: Optional positions for labeling

    Returns:
        Comparison results sorted by accessibility
    """
    results = []

    for i, seq in enumerate(sequences):
        prediction = predict_rna_structure(seq)
        prediction["site_id"] = i + 1
        prediction["site_position"] = (
            site_positions[i] if site_positions and i < len(site_positions) else i + 1
        )
        results.append(prediction)

    # Sort by accessibility score (descending)
    results.sort(
        key=lambda x: (
            x["accessibility_prediction"]["score"]
            if isinstance(x["accessibility_prediction"], dict)
            else x["accessibility_prediction"]["score"]
        ),
        reverse=True,
    )

    return {
        "sites_analyzed": len(results),
        "most_accessible": results[0] if results else None,
        "least_accessible": results[-1] if results else None,
        "all_sites": results,
        "recommendation": f"Target site {results[0]['site_position']} (position {results[0]['site_position']}) is the most accessible for siRNA binding"
        if results
        else "No sites to compare",
    }


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("RNA Secondary Structure Prediction Demo")
    print("=" * 60)

    test_sequences = [
        "ATGGACTACAAGGACGACGA",
        "GCGCGCGCGCGCGCGCGCGC",
        "AUGCGAUAGCUAUCGAUCGAU",
        "ACUGACUGACUGACUGACUGA",
    ]

    for i, seq in enumerate(test_sequences):
        print(f"\nSequence {i + 1}: {seq}")
        result = predict_rna_structure(seq)
        print(f"Dot-Bracket: {result['dot_bracket']}")
        print(f"Base Pairs: {result['num_base_pairs']}")
        print(f"Structure Score: {result['structure_score']}")
        print(f"Accessibility: {result['accessibility_prediction']}")
        print("-" * 40)
