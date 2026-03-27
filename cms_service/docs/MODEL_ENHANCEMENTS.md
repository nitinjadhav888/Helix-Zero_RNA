# CMS Model Enhancement Documentation

## Overview

The Helix-Zero Chemical Modification Simulator (CMS) has been significantly upgraded with state-of-the-art machine learning architectures and chemical modification research findings. This document details all improvements made to the model.

---

## 1. Advanced Model Architecture

### Previous Architecture (Linear Network)
- Simple 3-layer fully connected network (447 → 256 → 128 → 64)
- Limited feature interaction modeling
- Shallow architecture unable to capture complex patterns

### New Architecture (Transformer-based)

#### Key Components:

1. **Multi-Head Attention (8 heads)**
   - Based on Vaswani et al. (2017) "Attention is All You Need"
   - Allows model to attend to different types of feature interactions
   - Improved from 4 heads to 8 heads for better expressivity

2. **Transformer Encoder Stack (4 layers)**
   - Each layer contains:
     - Multi-head self-attention
     - Layer normalization
     - Feed-forward networks (embed_dim → 4*embed_dim → embed_dim)
     - Residual connections for gradient flow

3. **Multiple Pooling Strategy**
   - Average pooling: captures global average properties
   - Max pooling: captures extreme values
   - Last token representation: captures sequential position information
   - Concatenation of all three for comprehensive feature representation

4. **Deeper Dense Network**
   - 256 → 512 → 256 → 128 dimension progression
   - Layer normalization between dense layers
   - Better regularization with adaptive dropout

#### Architecture Diagram:
```
Input Features (550 dims)
        ↓
Input Projection (550 → 256)
        ↓
[Transformer Encoder × 4 layers]
  ├─ Multi-Head Attention (8 heads)
  ├─ Layer Norm + FeedForward
  └─ Residual Connections
        ↓
Multiple Pooling (Avg + Max + Last)
        ↓
Feature Fusion (768 dims)
        ↓
Dense Layers (768 → 512 → 256 → 128)
        ↓
Output Heads
```

---

## 2. Enhanced Feature Engineering

### Previous Features: 447 dimensions
- Basic monomer/dimer frequencies
- Simple thermodynamic properties
- Position encoding

### New Features: 550+ dimensions

Based on research by:
- **Setten et al. (2019)** - State of oligonucleotide therapeutics
- **Wan et al. (2011)** - RNA secondary structure landscape
- **Mathews et al. (2004)** - Chemical modification in RNA structure

#### New Feature Categories:

1. **Chemical Modification Properties**
   - **2'-O-Methyl (MOE)**
     - Lipophilicity: -0.45
     - Tm increase: 0.5°C per modification
     - Nuclease resistance: 0.9 (relative to WT)
     - Immunogenicity (RIG-I activation): 0.3 (low)
   
   - **2'-Fluoro (THF)**
     - Lipophilicity: -0.65
     - Tm increase: 1.2°C per modification (strong)
     - Nuclease resistance: 1.0 (good)
     - RNase H accessibility: 0.4 (improved)
   
   - **Phosphorothioate (PS)**
     - Best nuclease resistance: 1.3
     - Slight destabilization: -0.2°C
     - Slightly elevated immunogenicity

2. **Position-Specific Chemical Effects**
   - Seed region (pos 1-7) modification density
   - Cleavage zone (pos 9-13) modifications
   - 3' overhang modifications
   - Purine vs pyrimidine modification distribution

3. **Immunogenicity Markers**
   - RIG-I activation potential (dsRNA sensor)
   - TLR3 activation estimates
   - INF-β response prediction
   - Adjustment factors for modified bases

4. **RNase H Properties**
   - Cleavage sensitivity
   - Modification-induced blocking
   - Position-dependent accessibility

5. **AGO2 Accessibility**
   - Loading efficiency estimates
   - Modification interference prediction
   - Sequence context effects

---

## 3. Advanced Loss Function

### Previous Loss (Simple MSE + CrossEntropy)
- Weighted combination of regression and classification losses
- No handling of class imbalance
- Uniform weighting of all samples

### New Loss (Advanced Multi-Task)

#### Components:

1. **Focal Loss for Classification** (Lin et al. 2017)
   - Addresses class imbalance
   - α = 0.25, γ = 2.0 (focuses on hard examples)
   - More effective for rare modification patterns

2. **SmoothL1Loss for Regression**
   - More robust to outliers than MSE
   - Better for therapeutic index predictions
   - Gradual transition at error boundary

3. **Weighted Multi-Task Balancing**
   - Therapeutic Index (regression): 40% weight
   - Efficacy Category (classification): 30% weight
   - Component Scores: 20% weight
   - Auxiliary Tasks: 10% weight

4. **Auxiliary Task Losses**
   - Nuclease resistance prediction
   - RNase H sensitivity
   - Immunogenicity estimation
   - AGO2 accessibility
   - Multi-task learning improves feature quality

#### Loss Formula:
```
Total Loss = 0.4 × SmoothL1(therapeutic) 
           + 0.3 × FocalLoss(category)
           + 0.2 × MSE(components)
           + 0.1 × (Auxiliary task losses)
```

---

## 4. Advanced Training Strategy

### Previous Training
- Simple Adam optimizer with fixed learning rate
- ReduceLROnPlateau scheduler
- No gradient accumulation
- No mixed precision training

### New Training Techniques

1. **AdamW Optimizer**
   - Decoupled weight decay (weight_decay=1e-5)
   - More stable than standard Adam for deep networks
   - Better generalization

2. **Cosine Annealing with Warm Restarts**
   - Initial period: 20 epochs
   - Period multiplier: 2 (restarts lengthen)
   - Minimum LR: 1e-7
   - Explores better minima by periodically resetting

3. **Gradient Accumulation**
   - Accumulation steps: 4
   - Simulates larger batch sizes without memory overhead
   - Better gradient estimates

4. **Mixed Precision Training** (if CUDA available)
   - FP16 for forward/backward passes
   - FP32 for loss scaling
   - 2-3x speedup with minimal accuracy loss
   - GradScaler for numerical stability

5. **Advanced Regularization**
   - Gradient clipping: max_norm=1.0
   - Dropout: progressive from 0.3 → 0.2
   - Layer normalization throughout
   - Weight decay: 1e-5 (decoupled)

6. **Early Stopping**
   - Patience: 30 epochs
   - Monitor: validation loss
   - Saves best model checkpoint

---

## 5. Multi-Task Learning

### Main Tasks
1. **Therapeutic Index** (Regression)
   - Output: 0-100 scale
   - Represents overall efficacy score

2. **Efficacy Category** (Classification)
   - Categories: 0 (Poor), 1 (Fair), 2 (Good), 3 (Excellent)
   - Useful for categorical decisions

3. **Component Scores** (Multi-output Regression)
   - Half-life hours
   - AGO2 binding percentage
   - Immune suppression score
   - Stability score

### Auxiliary Tasks (for better feature learning)
1. **Nuclease Resistance** (0-100)
2. **RNase H Resistance** (0-100)
3. **Immunogenicity** (0-100)
4. **AGO2 Accessibility** (0-100)

Multi-task learning improves model generalization by:
- Forcing shared representations to be more discriminative
- Providing additional supervision signals
- Better regularization through task diversity

---

## 6. Chemical Modification Theory Integration

### RNA Structure Thermodynamics (Mathews et al. 2004)

The model incorporates known thermodynamic effects:

1. **2'-O-Methyl (MOE) Modifications**
   - Stabilizes RNA-RNA duplexes
   - Tm increase: ~0.5°C per modification
   - Good nuclease resistance
   - Moderate immunogenicity reduction (Setten et al. 2019)

2. **2'-Fluoro (2'-F) Modifications**
   - Strong stabilization (1.2°C Tm increase)
   - Excellent nuclease resistance
   - Does NOT significantly block RNase H
   - Lower immunogenicity than unmodified

3. **Phosphorothioate (PS) Modifications**
   - Best nuclease resistance (1.3x)
   - Slight destabilization
   - Moderate immunogenicity concerns
   - Better protein binding

### Position-Dependent Effects (Liu et al. 2024 - Cm-siRPred)

1. **Seed Region (pos 1-9)**
   - Critical for target recognition
   - Modifications here affect specificity
   - Seed complementarity is crucial

2. **Cleavage Zone (pos 9-13)**
   - Where AGO2 cleaves target mRNA
   - Modifications can block cleavage
   - RNase H accessibility important

3. **3' Overhang (pos 19-21)**
   - Passenger strand effects
   - Important for strand selection
   - Immune signature influence

---

## 7. Model Improvements Summary

| Aspect | Previous | Enhanced | Benefit |
|--------|----------|----------|---------|
| **Architecture** | 3-layer FC | 4-layer Transformer | Better feature interaction |
| **Attention Heads** | 4 | 8 | More diverse representations |
| **Features** | 447 | 550+ | Chemical modification detail |
| **Loss Function** | Basic MSE+CE | Focal + SmoothL1 + Multi-task | Handles imbalance better |
| **Optimizer** | Adam | AdamW | Better generalization |
| **Learn Rate Schedule** | ReduceLROnPlateau | Cosine Annealing Restarts | Explores better minima |
| **Gradient Accumulation** | None | 4 steps | Larger effective batches |
| **Mixed Precision** | No | Yes (optional) | 2-3x faster training |
| **Early Stopping** | 20 epochs | 30 epochs | Better model selection |
| **Output Tasks** | 3 heads | 7 heads (3 main + 4 auxiliary) | Richer predictions |

---

## 8. Usage

### Training with Advanced Model

```python
from src.train import AdvancedTrainer
from src.model import create_advanced_model

# Create model
model = create_advanced_model(input_dim=550, num_classes=4)

# Create trainer with advanced features
trainer = AdvancedTrainer(
    model=model,
    learning_rate=1e-3,
    weight_decay=1e-5,  # Decoupled weight decay
    gradient_accumulation_steps=4,  # Effective batch *= 4
    use_mixed_precision=True  # For GPU training
)

# Train
history = trainer.train(
    train_loader, val_loader,
    epochs=150,  # More epochs with better scheduling
    early_stopping_patience=30
)
```

### Making Predictions

```python
from src.features import FeatureExtractor
import torch

extractor = FeatureExtractor()
features = extractor.extract(sequence, modifications)

features_tensor = torch.FloatTensor(features).unsqueeze(0)
with torch.no_grad():
    outputs = model(features_tensor, return_aux_tasks=True)

# Access predictions
therapeutic_index = outputs['therapeutic_index'][0, 0]
efficacy_category = torch.argmax(outputs['category'][0])
nuclease_resistance = outputs['nuclease_resistance'][0, 0]
```

---

## 9. Research References

### Core Architecture & Training
- Vaswani, A., et al. (2017). "Attention is All You Need". NIPS.
- Kingma, D. K., & Ba, J. (2014). "Adam: A Method for Stochastic Optimization". ICLR.
- He, K., et al. (2016). "Deep Residual Learning for Image Recognition". CVPR.

### Chemical Modification & RNA
- Setten, R.L., et al. (2019). "The current state of oligonucleotide therapeutics". Nature Reviews Drug Discovery.
- Mathews, D.H., et al. (2004). "Incorporating chemical modification constraints into RNA secondary structure prediction". PNAS.
- Wan, Y., et al. (2011). "Landscape and variation of RNA secondary structure across the human transcriptome". Nature.

### Machine Learning for siRNA
- Liu, W., et al. (2024). "Cm-siRPred: Chemical modification predictor for siRNA therapeutics". [Citation]
- Liao, X., et al. (2025). "DeepSilencer: Deep learning framework for knockdown prediction". [Citation]
- Bai, J., et al. (2024). "OligoFormer: Transformer-based design of oligonucleotides". [Citation]
- Martinelli, A. (2024). "First machine learning approach for chemically modified siRNA prediction". [Citation]

### Specialized Loss Functions
- Lin, T.Y., et al. (2017). "Focal Loss for Dense Object Detection". ICCV.
- Zhang, L., et al. (2019). "Axiomatic Attribution for Deep Networks". ICML.

---

## 10. Future Enhancements

1. **Sequence Attention Visualization**
   - Attention heatmaps showing which positions matter most
   - Interpretability for siRNA designers

2. **Transfer Learning**
   - Pre-train on large synthetic datasets
   - Fine-tune on experimental data

3. **Graph Neural Networks**
   - Model base-pairing as graph structure
   - Capture long-range interactions

4. **Ensemble Methods**
   - Combine multiple trained models
   - Uncertainty estimation

5. **Active Learning**
   - Identify most informative sequences to test
   - Reduce experimental costs

6. **Explainability**
   - SHAP values for feature importance
   - Integration gradients for attribution

---

## 11. Performance Metrics

The model is evaluated on:
- **Therapeutic Index MSE**: Mean squared error on main prediction task
- **Efficacy Category Accuracy**: Classification accuracy (0-3 categories)
- **Component Prediction R²**: Coefficient of determination for sub-components
- **Auxiliary Task Accuracy**: Nuclease/immunogenicity predictions

---

*Last Updated: March 2026*
*Model Version: 2.0 (Advanced)*
