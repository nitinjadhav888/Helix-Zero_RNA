"""
Helix-Zero CMS :: Feature Extraction Module

Based on Cm-siRPred multi-view learning strategy:
- Liu et al. (2024) Cm-siRPred
- Serov et al. (2025) Meta-learning pipeline

Implements:
1. Sequence-based features
2. Thermodynamic features
3. Chemical descriptor features
4. Structural features
"""

import numpy as np
from typing import Dict, List
from src.data_structures import siRNAsequence, ModificationType


class FeatureExtractor:
    """
    Feature extraction for CMS model.

    Implements multi-view learning strategy from Cm-siRPred:
    - View 1: Sequence composition
    - View 2: Thermodynamic properties
    - View 3: Chemical modification descriptors
    """

    def __init__(self, max_length: int = 21):
        self.max_length = max_length
        self.kmer_to_idx = self._build_kmer_dict()

    def extract(self, sequence: siRNAsequence, modifications: List) -> np.ndarray:
        """
        Extract all features from sequence and modifications.

        Returns:
            Feature vector of shape (n_features,)
        """
        features = []

        features.extend(self._sequence_features(sequence))
        features.extend(self._thermodynamic_features(sequence))
        features.extend(self._positional_features(sequence))
        features.extend(self._chemical_features(sequence, modifications))

        return np.array(features, dtype=np.float32)

    def _sequence_features(self, sequence: siRNAsequence) -> List[float]:
        """Extract sequence composition features."""
        seq = sequence.sequence
        length = len(seq)

        features = []

        for base in "AUCG":
            features.append(seq.count(base) / length)

        for d1 in "AUCG":
            for d2 in "AUCG":
                dinuc = d1 + d2
                count = sum(1 for i in range(length - 1) if seq[i : i + 2] == dinuc)
                features.append(count / max(length - 1, 1))

        gc = sum(1 for b in seq if b in "GC")
        features.append(gc / length)

        purines = sum(1 for b in seq if b in "AG")
        pyrimidines = sum(1 for b in seq if b in "UC")
        features.append(purines / pyrimidines if pyrimidines > 0 else 0)

        return features

    def _thermodynamic_features(self, sequence: siRNAsequence) -> List[float]:
        """Extract thermodynamic features."""
        from src.calculations import (
            calculate_mfe,
            calculate_melting_temperature,
            calculate_thermodynamic_asymmetry,
        )

        seq = sequence.sequence

        features = []

        features.append(calculate_mfe(seq))
        features.append(calculate_melting_temperature(seq))
        features.append(calculate_thermodynamic_asymmetry(seq))

        for end_len in [4, 3, 2]:
            for end_type in ["start", "end"]:
                if end_type == "start":
                    end_seq = seq[:end_len]
                else:
                    end_seq = seq[-end_len:]

                if len(end_seq) >= 2:
                    mfe = calculate_mfe(end_seq)
                    features.append(mfe)
                else:
                    features.append(0.0)

        return features

    def _positional_features(self, sequence: siRNAsequence) -> List[float]:
        """Extract position-specific features."""
        seq = sequence.sequence

        base_to_idx = {"A": 0, "U": 1, "C": 2, "G": 3}

        features = []
        for i in range(self.max_length):
            if i < len(seq):
                one_hot = [0.0] * 4
                one_hot[base_to_idx.get(seq[i], 0)] = 1.0
                features.extend(one_hot)
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])

        for i in range(self.max_length):
            if i == 1:
                features.append(2.0)
            elif i in range(9, 13):
                features.append(0.0)
            elif i >= 19:
                features.append(1.5)
            else:
                features.append(1.0)

        return features

    def _chemical_features(
        self, sequence: siRNAsequence, modifications: List
    ) -> List[float]:
        """Extract chemical modification descriptors."""
        features = []

        features.append(len(modifications))

        for i in range(self.max_length):
            features.append(1.0 if i in modifications else 0.0)

        pyrimidine_mods = sum(
            1 for pos in modifications if sequence.get_base(pos) in "UC"
        )
        purine_mods = len(modifications) - pyrimidine_mods

        features.append(pyrimidine_mods)
        features.append(purine_mods)
        features.append(pyrimidine_mods / len(modifications) if modifications else 0.0)

        features.append(len(modifications) / sequence.length)

        return features

    def _build_kmer_dict(self) -> Dict[str, int]:
        """Build k-mer to index mapping."""
        kmers = []
        for k in [2, 3]:
            for seq in self._generate_kmers("AUCG", k):
                kmers.append(seq)

        return {kmer: idx for idx, kmer in enumerate(kmers)}

    def _generate_kmers(self, alphabet: str, k: int) -> List[str]:
        """Generate all k-mers for an alphabet."""
        if k == 1:
            return list(alphabet)

        smaller = self._generate_kmers(alphabet, k - 1)
        return [c + s for c in alphabet for s in smaller]

    def get_feature_names(self) -> List[str]:
        """Get names of all features (for interpretability)."""
        names = []

        for base in "AUCG":
            names.append(f"freq_{base}")

        for d1 in "AUCG":
            for d2 in "AUCG":
                names.append(f"dinuc_{d1}{d2}")

        names.extend(["gc_content", "purine_pyrimidine_ratio"])

        names.extend(
            [
                "mfe",
                "tm",
                "asymmetry",
                "end5_4nt_mfe",
                "end3_4nt_mfe",
                "end5_3nt_mfe",
                "end3_3nt_mfe",
                "end5_2nt_mfe",
                "end3_2nt_mfe",
            ]
        )

        for i in range(self.max_length):
            names.extend([f"pos{i}_{b}" for b in "AUCG"])

        for i in range(self.max_length):
            names.append(f"pos_weight_{i}")

        names.extend(
            [
                "num_modifications",
            ]
        )

        for i in range(self.max_length):
            names.append(f"mod_pos_{i}")

        names.extend(
            [
                "pyrimidine_mods",
                "purine_mods",
                "pyrimidine_mod_ratio",
                "modification_density",
            ]
        )

        return names

    @property
    def feature_dim(self) -> int:
        """Get total number of features."""
        return len(self.get_feature_names())
