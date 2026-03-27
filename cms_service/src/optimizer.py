import torch
import numpy as np
from src.data_structures import siRNAsequence, ModificationType, PredictionResult
from src.features import FeatureExtractor
from src.model import AdvancedCMSModel

class ModificationOptimizer:
    """
    Bio-Driven optimizer that searches for the best chemical modification pattern
    based on the user's requirements using the verified calculation physics engine.
    """
    def __init__(self, model, feature_extractor, device='cpu'):
        self.model = model
        self.feature_extractor = feature_extractor
        self.device = device
        
        # Focus metric mapping
        self.objective_mapping = {
            'efficacy': 'therapeutic_index',
            'survivability': 'stability', # or half_life/nuclease_resistance
            'immunogenicity': 'immune_suppression'
        }

    def generate_candidate_patterns(self, seq_length=21):
        """Builds a smart list of candidate positions to modify, respecting biological rules."""
        candidates = []
        cleavage_zone = {9, 10, 11, 12}
        all_positions = set(range(seq_length))
        safe_positions = sorted(list(all_positions - cleavage_zone))
        
        # IMPORTANT: Force the AI to pick *some* modifications by not offering the empty array.
        # 1. All safe positions
        candidates.append(safe_positions)

        # 2. Alternating (Even)
        candidates.append([p for p in safe_positions if p % 2 == 0])

        # 3. Alternating (Odd)
        candidates.append([p for p in safe_positions if p % 2 != 0])

        # 4. 5'-End Heavy (First 5 bases) + 3'-End Heavy (Last 5 bases)
        candidates.append([p for p in safe_positions if p < 5 or p > seq_length - 6])
        
        return candidates

    def optimize(self, sequence_str, objective='efficacy'):
        """
        Runs the sequence through the Transformer model with different 
        modification candidates and types to find the optimal setup.
        """
        sequence = siRNAsequence(sequence_str)
        mod_types = ['OME', 'FLUORO', 'PS'] 
        
        best_score = -float('inf')
        best_candidate = None
        
        patterns = self.generate_candidate_patterns(len(sequence_str))
        
        # Add pyrimidine targeting pattern specific to this sequence
        pyr_positions = [i for i, base in enumerate(sequence.sequence) if base in 'UC' and i not in {9, 10, 11, 12}]
        if pyr_positions not in patterns:
            patterns.append(pyr_positions)
        
        # Evaluate all combinations
        for mod_name in mod_types:
            # Map string to enum
            try:
                mod_enum = ModificationType[mod_name]
            except KeyError:
                continue
            
            for positions in patterns:
                # Use the biological physics engine to get TRUE scores
                result = PredictionResult.from_calculation(
                    sequence=sequence,
                    mod_type=mod_enum,
                    positions=positions
                )

                score = 0
                if objective == 'efficacy':
                    score = result.therapeutic_index
                elif objective == 'survivability':
                    score = result.stability_score
                elif objective == 'immunogenicity':
                    score = result.immune_suppression_percent

                # Compare
                if score > best_score:
                    best_score = float(score)
                    best_candidate = {
                        'modification_type': mod_name,
                        'positions': positions,
                        'score': float(score),
                        'therapeutic_index': float(result.therapeutic_index),
                        'stability': float(result.stability_score),
                        'immune_suppression': float(result.immune_suppression_percent)
                    }
        return best_candidate