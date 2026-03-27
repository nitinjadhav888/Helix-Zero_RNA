"""
Helix-Zero CMS :: Machine Learning Model

Based on:
- Cm-siRPred architecture (Liu et al. 2024)
- OligoFormer (Bai et al. 2024)

Architecture:
- Feature extraction (multi-view)
- Multi-layer neural network
- Multi-task prediction heads
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple
import numpy as np


class CMSModel(nn.Module):
    """
    Chemical Modification Simulator Neural Network.

    Architecture:
    ┌─────────────────────────────────────────┐
    │  Input Features (193 dims)               │
    ├─────────────────────────────────────────┤
    │  Dense Layer 1 (193 → 128)              │
    │  + BatchNorm + ReLU + Dropout(0.3)     │
    ├─────────────────────────────────────────┤
    │  Dense Layer 2 (128 → 64)               │
    │  + BatchNorm + ReLU + Dropout(0.3)     │
    ├─────────────────────────────────────────┤
    │  Dense Layer 3 (64 → 32)                │
    │  + BatchNorm + ReLU                    │
    ├─────────────────────────────────────────┤
    │  Output Heads:                          │
    │  ├─ Therapeutic Index (regression)     │
    │  ├─ Efficacy Category (classification)  │
    │  └─ Component Scores (multi-output)     │
    └─────────────────────────────────────────┘
    """

    def __init__(self, input_dim: int = 193, num_classes: int = 4):
        super().__init__()

        self.fc1 = nn.Linear(input_dim, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.dropout1 = nn.Dropout(0.3)

        self.fc2 = nn.Linear(128, 64)
        self.bn2 = nn.BatchNorm1d(64)
        self.dropout2 = nn.Dropout(0.3)

        self.fc3 = nn.Linear(64, 32)
        self.bn3 = nn.BatchNorm1d(32)

        self.therapeutic_head = nn.Linear(32, 1)
        self.category_head = nn.Linear(32, num_classes)
        self.component_head = nn.Linear(32, 4)

        self._init_weights()

    def _init_weights(self):
        """Xavier/Glorot initialization."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass.

        Args:
            x: Input features of shape (batch_size, input_dim)

        Returns:
            Dictionary with predictions:
            - therapeutic_index: Regression output (0-100)
            - category_logits: Classification logits (batch_size, num_classes)
            - components: Multi-output scores [half_life, ago2, immune, stability]
        """
        x = self.fc1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.dropout2(x)

        x = self.fc3(x)
        x = self.bn3(x)
        x = F.relu(x)

        therapeutic = torch.sigmoid(self.therapeutic_head(x)) * 100
        category_logits = self.category_head(x)
        components = torch.sigmoid(self.component_head(x)) * 100

        return {
            "therapeutic_index": therapeutic.squeeze(-1),
            "category_logits": category_logits,
            "components": components,
        }

    def predict(self, x: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Predict with numpy arrays.

        Args:
            x: Input features of shape (batch_size, input_dim)

        Returns:
            Dictionary with predictions
        """
        self.eval()
        with torch.no_grad():
            x_tensor = torch.FloatTensor(x)
            outputs = self.forward(x_tensor)

            return {
                "therapeutic_index": outputs["therapeutic_index"].numpy(),
                "category_probs": F.softmax(outputs["category_logits"], dim=-1).numpy(),
                "components": outputs["components"].numpy(),
            }


class CMSLoss(nn.Module):
    """
    Multi-task loss for CMS model.

    Combines:
    1. Regression loss (Therapeutic Index)
    2. Classification loss (Efficacy category)
    3. Component regression loss
    """

    def __init__(
        self, reg_weight: float = 0.5, cls_weight: float = 0.3, comp_weight: float = 0.2
    ):
        super().__init__()
        self.reg_weight = reg_weight
        self.cls_weight = cls_weight
        self.comp_weight = comp_weight
        self.mse = nn.MSELoss()
        self.ce = nn.CrossEntropyLoss()

    def forward(
        self, predictions: Dict[str, torch.Tensor], targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Calculate combined loss.

        Args:
            predictions: Model outputs
            targets: Ground truth values
        """
        reg_loss = self.mse(
            predictions["therapeutic_index"], targets["therapeutic_index"]
        )

        cls_loss = self.ce(predictions["category_logits"], targets["category"].long())

        comp_loss = self.mse(predictions["components"], targets["components"])

        total_loss = (
            self.reg_weight * reg_loss
            + self.cls_weight * cls_loss
            + self.comp_weight * comp_loss
        )

        return total_loss


def create_model(input_dim: int = 193, num_classes: int = 4) -> CMSModel:
    """Factory function to create a new CMS model."""
    return CMSModel(input_dim=input_dim, num_classes=num_classes)


def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters in model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
