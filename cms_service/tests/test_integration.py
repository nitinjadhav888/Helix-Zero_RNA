"""
Integration tests for complete CMS pipeline.
"""

import pytest
import torch
from src.data_structures import siRNAsequence, ModificationType, ModificationProfile
from src.calculations import calculate_therapeutic_index
from src.features import FeatureExtractor
from src.model import AdvancedCMSModel, create_advanced_model


class TestEndToEnd:
    """End-to-end pipeline tests."""
    
    def test_complete_pipeline(self):
        """Test complete CMS pipeline."""
        # Input
        sequence = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        modifications = [(0, ModificationType.OME), (1, ModificationType.OME),
                        (5, ModificationType.OME), (6, ModificationType.OME),
                        (19, ModificationType.OME)]
        
        positions = [pos for pos, _ in modifications]
        
        # Feature extraction
        extractor = FeatureExtractor()
        features = extractor.extract(sequence, positions)
        
        assert features.shape[0] > 0
        assert not torch.isnan(torch.tensor(features)).any()
        
        # Model prediction
        model = create_advanced_model(input_dim=features.shape[0])
        model.eval()
        
        with torch.no_grad():
            x = torch.FloatTensor(features).unsqueeze(0)
            predictions = model(x)
        
        assert 'therapeutic_index' in predictions
        assert 'category' in predictions
        assert 'components' in predictions
        
        # Check prediction ranges
        ti = predictions['therapeutic_index'].item()
        assert 0 <= ti <= 100
    
    def test_constraint_enforcement(self):
        """Test that cleavage zone violations are penalized."""
        from src.calculations import calculate_ago2_binding, CLEAVAGE_ZONE
        
        seq = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        
        # Test with violation
        profile = ModificationProfile.from_type(ModificationType.OME)
        violation_positions = [9, 10, 11, 12]  # All cleavage zone
        
        ago2_violation = calculate_ago2_binding(seq, violation_positions, profile)
        
        # Test without violation
        safe_positions = [0, 1, 2, 3]  # Outside cleavage zone
        ago2_safe = calculate_ago2_binding(seq, safe_positions, profile)
        
        # Violation should significantly reduce Ago2 binding
        assert ago2_violation < ago2_safe - 20


class TestModelBehavior:
    """Test model behavior on edge cases."""
    
    def test_unmodified_sequence(self):
        """Test with no modifications."""
        seq = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        
        # No modifications
        positions = []
        
        from src.calculations import (
            calculate_half_life, calculate_ago2_binding,
            calculate_immune_suppression
        )
        from src.data_structures import ModificationProfile
        
        profile = ModificationProfile.from_type(ModificationType.OME)
        
        half_life = calculate_half_life(seq, positions, profile)
        ago2 = calculate_ago2_binding(seq, positions, profile)
        immune = calculate_immune_suppression(seq, positions, profile)
        
        # Unmodified should have base nuclease factor (0.5)
        assert half_life == 0.5
        
        # Full Ago2 binding (no modifications)
        assert ago2 == 100.0
        
        # No immune suppression
        assert immune == 0.0
    
    def test_all_pyrimidine_modification(self):
        """Test modification of all pyrimidines."""
        seq = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        
        # All pyrimidines
        positions = [i for i, b in enumerate(seq.sequence) if b in 'UC']
        
        from src.calculations import calculate_half_life
        from src.data_structures import ModificationProfile, ModificationType
        
        profile = ModificationProfile.from_type(ModificationType.OME)
        half_life = calculate_half_life(seq, positions, profile)
        
        # Pyrimidines get 1.5× boost per nt
        num_pyrimidines = len(positions)
        expected_boost = num_pyrimidines * 1.5 * profile.stability_boost_per_nt
        
        # HalfLife = 0.5 (nuclease) + boost
        expected = 0.5 + expected_boost
        
        assert abs(half_life - expected) < 0.1