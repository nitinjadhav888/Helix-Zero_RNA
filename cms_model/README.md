# Helix-Zero CMS (Chemical Modification Simulator)

AI-powered siRNA chemical modification optimization for species-specific pesticides.

## Quick Start

### 1. Install Dependencies

```bash
cd cms_model
pip install -r requirements.txt
```

### 2. Train the Model

```bash
cd cms_model
python -m src.train
```

### 3. Use the Model

```python
from src.data_structures import siRNAsequence, ModificationType
from src.calculations import calculate_half_life, calculate_ago2_binding, calculate_therapeutic_index
from src.data_structures import ModificationProfile

seq = siRNAsequence("GUCAUCACGGUGUACCUCATT")
profile = ModificationProfile.from_type(ModificationType.OME)
positions = [0, 2, 4, 6, 14, 16, 18]

half_life = calculate_half_life(seq, positions, profile)
ago2 = calculate_ago2_binding(seq, positions, profile)
ti = calculate_therapeutic_index(half_life, ago2)

print(f"Half-life: {half_life}h")
print(f"Ago2 binding: {ago2}%")
print(f"Therapeutic Index: {ti}")
```

## Directory Structure

```
cms_model/
├── src/
│   ├── __init__.py          # Package init
│   ├── data_structures.py   # Core data types
│   ├── calculations.py      # Thermodynamic calculations
│   ├── features.py           # Feature extraction
│   ├── model.py              # Neural network model
│   └── train.py              # Training pipeline
├── data/                     # Training data
├── models/                   # Saved models
├── tests/                    # Unit tests
└── requirements.txt
```

## Scientific Basis

| Parameter | Source | Confidence |
|-----------|--------|------------|
| Stability boost | Bramsen 2009 Fig 5a | HIGH |
| Ago2 penalty | Bramsen 2009 Table 1 | HIGH |
| Nuclease resistance | Bramsen 2009 | HIGH |
| Immune suppression | Choung 2006 | HIGH |

## References

- Bramsen JB et al. (2009) NAR 38:7688
- Jackson AL et al. (2006) RNA 12:1197
- Liu T et al. (2024) Int J Biol Macromol 264:130638
- Martinelli DD (2024) Genomics 116:110815
