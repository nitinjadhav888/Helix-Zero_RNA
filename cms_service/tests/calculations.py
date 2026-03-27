"""
Unit tests for CMS calculations.
"""

import pytest
import numpy as np
from src.calculations import (
    calculate_mfe,
    calculate_melting_temperature,
    calculate_thermodynamic_asymmetry,
    calculate_half_life,
    calculate_ago2_binding,
    calculate_immune_suppression,
    calculate_therapeutic_index
)
from src.data_structures import siRNAsequence, ModificationProfile, ModificationType


class TestThermodynamicCalculations:
    """Test thermodynamic calculations."""
    
    def test_mfe_calculation(self):
        """Test MFE calculation for known sequence."""
        seq = "GCGCGCGCGCGCGCGCGCGC"
        mfe = calculate_mfe(seq)
        
        # GC-rich sequence should have negative MFE
        assert mfe < 0
        assert -50 < mfe < -20  # Expected range
    
    def test_mfe_with_au_rich(self):
        """Test MFE for AU-rich sequence."""
        seq = "AUAUAUAUAUAUAUAUAUAU"
        mfe = calculate_mfe(seq)
        
        # AU-rich should be less stable
        assert mfe < 0
        assert mfe > calculate_mfe("GCGCGCGCGCGCGCGCGCGC")
    
    def test_asymmetry_calculation(self):
        """Test thermodynamic asymmetry."""
        # Strong 5', weak 3' - good for RISC loading
        seq = "GCGCGCGCGCGCGCGCGCGC"
        asymmetry = calculate_thermodynamic_asymmetry(seq)
        
        # Should be positive (3' end is weaker)
        assert asymmetry > 0


class TestCMSCalculations:
    """Test CMS-specific calculations."""
    
    def test_half_life_ome(self):
        """Test half-life calculation with 2'-OMe."""
        seq = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        profile = ModificationProfile.from_type(ModificationType.OME)
        
        positions = [0, 1, 5, 6, 19, 20]  # Modified positions
        half_life = calculate_half_life(seq, positions, profile)
        
        # Should be higher than unmodified
        assert half_life > 0.5  # Base nuclease factor
        
        # 2'-OMe should add ~2.5 hrs per pyrimidine modification
        # We modified 4 pyrimidines + 2 purines
        assert 10 < half_life < 30  # Expected range
    
    def test_ago2_cleavage_zone_violation(self):
        """Test Ago2 penalty for cleavage zone modification."""
        seq = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        profile = ModificationProfile.from_type(ModificationType.OME)
        
        # Violation: Position 10 (cleavage zone)
        positions_with_violation = [10]
        ago2_with = calculate_ago2_binding(seq, positions_with_violation, profile)
        
        # No violation
        positions_no_violation = [1]  # Position 2 (seed region)
        ago2_without = calculate_ago2_binding(seq, positions_no_violation, profile)
        
        # Cleavage zone violation should severely reduce Ago2 binding
        assert ago2_with < ago2_without - 20  # At least 25% penalty
    
    def test_immune_suppression_ps(self):
        """Test immune suppression with PS modification."""
        seq = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        profile = ModificationProfile.from_type(ModificationType.PS)
        
        positions = [0, 5, 10, 15, 20]
        immune = calculate_immune_suppression(seq, positions, profile)
        
        # PS has immune factor 0.20, 5/21 positions modified
        expected = 0.20 * (5/21) * 100
        assert abs(immune - expected) < 1.0
    
    def test_therapeutic_index_calculation(self):
        """Test therapeutic index formula."""
        half_life = 24.0  # 24 hours
        ago2 = 85.0  # 85% binding
        
        ti = calculate_therapeutic_index(half_life, ago2)
        
        # Expected: (24/72 * 100 * 0.5) + (85 * 0.5)
        # = (33.33 * 0.5) + 42.5 = 16.67 + 42.5 = 59.17
        expected = (24/72 * 100 * 0.5) + (85 * 0.5)
        assert abs(ti - expected) < 0.1


class TestPositionRules:
    """Test critical position-specific rules."""
    
    def test_seed_region_position(self):
        """Test position 2 (seed region) is critical."""
        seq = siRNAsequence("AAGUAGUAAGCUAAGCUAAG")
        
        # Position 2 (index 1) should be in seed region
        from src.calculations import SEED_REGION
        assert 1 in SEED_REGION
    
    def test_cleavage_zone_protected(self):
        """Test cleavage zone positions are protected."""
        from src.calculations import CLEAVAGE_ZONE
        
        # Positions 9-12 (0-indexed) should be in cleavage zone
        assert CLEAVAGE_ZONE == {9, 10, 11, 12}
    
    def test_modification_profile_stability(self):
        """Test modification profiles have correct stability boosts."""
        ome_profile = ModificationProfile.from_type(ModificationType.OME)
        
        # 2'-OMe should have ~2.5 hrs/nt stability boost
        assert 2.0 < ome_profile.stability_boost_per_nt < 3.0
        
        # LNA should have higher stability boost
        lna_profile = ModificationProfile.from_type(ModificationType.LNA)
        assert lna_profile.stability_boost_per_nt > ome_profile.stability_boost_per_nt