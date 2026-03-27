"""
Helix-Zero CMS :: Training Module

Training pipeline for the Chemical Modification Simulator model.
"""

import os
import json
import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Tuple
from tqdm import tqdm

from src.model import CMSModel, CMSLoss, count_parameters
from src.features import FeatureExtractor
from src.data_structures import siRNAsequence, ModificationType, ModificationProfile


class CMSDataset(Dataset):
    """
    Dataset for CMS training.

    Expects data in format:
    {
        'sequence': 'AUCG...',
        'modifications': [0, 2, 4],  # positions
        'mod_type': '2_ome',
        'half_life': 8.5,
        'ago2': 75.0,
        'immune': 60.0,
        'therapeutic_index': 65.0,
        'category': 1  # 0=Poor, 1=Moderate, 2=Good, 3=Excellent
    }
    """

    def __init__(self, data: List[Dict], feature_extractor: FeatureExtractor):
        self.data = data
        self.feature_extractor = feature_extractor

        self.mod_type_map = {
            "2_ome": ModificationType.OME,
            "2_f": ModificationType.FLUORO,
            "ps": ModificationType.PS,
            "lna": ModificationType.LNA,
            "una": ModificationType.UNA,
        }

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(
        self, idx: int
    ) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]:
        item = self.data[idx]

        seq = siRNAsequence(item["sequence"])
        mod_type = self.mod_type_map.get(
            item.get("mod_type", "2_ome"), ModificationType.OME
        )
        positions = item.get("modifications", [])

        features = self.feature_extractor.extract(seq, positions)

        X = torch.FloatTensor(features)

        y_therapeutic = torch.FloatTensor([item.get("therapeutic_index", 0)])[0]
        y_category = torch.LongTensor([item.get("category", 0)])[0]
        y_components = torch.FloatTensor(
            [
                item.get("half_life", 0) / 72 * 100,
                item.get("ago2", 100),
                item.get("immune", 0),
                item.get("stability", 50),
            ]
        )

        return X, {
            "therapeutic_index": y_therapeutic,
            "category": y_category,
            "components": y_components,
        }


def generate_synthetic_data(n_samples: int = 1000) -> List[Dict]:
    """
    Generate synthetic training data based on literature parameters.

    This creates realistic training data following the patterns from:
    - Bramsen et al. (2009): 2160 siRNA screen
    - Jackson et al. (2006): Position 2 modification
    """
    np.random.seed(42)
    data = []

    sequences = [
        "GUCAUCACGGUGUACCUCAUU",
        "AUGGCCUAUUGAGAAGACAUU",
        "CGACGUGGACGGCCUCUUUUU",
        "UUCUCCGAACGUGUCACGUUU",
        "CCUACAUCCAGCAGCCACUUU",
    ]

    mod_types = ["2_ome", "2_f", "ps"]

    for i in range(n_samples):
        seq = sequences[i % len(sequences)]
        mod_type = mod_types[i % len(mod_types)]

        n_mods = np.random.randint(3, 12)
        positions = sorted(np.random.choice(range(21), n_mods, replace=False).tolist())

        profile = ModificationProfile.from_type(
            ModificationType.OME
            if mod_type == "2_ome"
            else ModificationType.FLUORO
            if mod_type == "2_f"
            else ModificationType.PS
        )

        pyrimidine_count = sum(1 for p in positions if seq[p] in "UC")
        purine_count = len(positions) - pyrimidine_count

        half_life = 0.5 * (1 + len(positions) / 21 * profile.nuclease_resistance)
        half_life += (
            pyrimidine_count + purine_count * 0.5
        ) * profile.stability_boost_per_nt
        half_life = min(half_life + np.random.normal(0, 0.5), 72)

        ago2_penalty = (
            pyrimidine_count * profile.ago2_penalty_per_pyrimidine
            + purine_count * profile.ago2_penalty_per_purine
        )
        ago2 = max(100 - ago2_penalty + np.random.normal(0, 5), 0)

        immune = profile.immune_suppression * (len(positions) / 21) * 100

        half_life_score = min(half_life / 72, 1.0) * 100
        therapeutic_index = half_life_score * 0.5 + ago2 * 0.5
        therapeutic_index += np.random.normal(0, 3)
        therapeutic_index = max(min(therapeutic_index, 100), 0)

        if therapeutic_index >= 70:
            category = 3
        elif therapeutic_index >= 50:
            category = 2
        elif therapeutic_index >= 30:
            category = 1
        else:
            category = 0

        data.append(
            {
                "sequence": seq,
                "modifications": positions,
                "mod_type": mod_type,
                "half_life": half_life,
                "ago2": ago2,
                "immune": immune,
                "stability": half_life_score,
                "therapeutic_index": therapeutic_index,
                "category": category,
            }
        )

    return data


def train_epoch(
    model: CMSModel,
    dataloader: DataLoader,
    criterion: CMSLoss,
    optimizer: optim.Optimizer,
    device: str = "cpu",
) -> Dict[str, float]:
    """Train for one epoch."""
    model.train()
    total_loss = 0
    n_batches = 0

    for X, y in dataloader:
        X = X.to(device)
        y = {k: v.to(device) for k, v in y.items()}

        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return {"loss": total_loss / n_batches}


def evaluate(
    model: CMSModel, dataloader: DataLoader, criterion: CMSLoss, device: str = "cpu"
) -> Dict[str, float]:
    """Evaluate model on validation set."""
    model.eval()
    total_loss = 0
    n_batches = 0

    with torch.no_grad():
        for X, y in dataloader:
            X = X.to(device)
            y = {k: v.to(device) for k, v in y.items()}

            outputs = model(X)
            loss = criterion(outputs, y)

            total_loss += loss.item()
            n_batches += 1

    return {"loss": total_loss / n_batches}


def train_model(
    train_data: List[Dict],
    val_data: List[Dict],
    feature_extractor: FeatureExtractor,
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    device: str = "cpu",
    save_path: str = "models/cms_model.pt",
) -> Dict[str, List[float]]:
    """
    Complete training pipeline.

    Args:
        train_data: Training samples
        val_data: Validation samples
        feature_extractor: Feature extractor
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        device: Device to train on
        save_path: Path to save best model

    Returns:
        Training history
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    train_dataset = CMSDataset(train_data, feature_extractor)
    val_dataset = CMSDataset(val_data, feature_extractor)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    model = CMSModel(input_dim=feature_extractor.feature_dim)
    model = model.to(device)

    criterion = CMSLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=5)

    history = {"train_loss": [], "val_loss": []}
    best_val_loss = float("inf")

    print(f"Training CMS Model")
    print(f"Parameters: {count_parameters(model):,}")
    print(f"Training samples: {len(train_data)}")
    print(f"Validation samples: {len(val_data)}")
    print("-" * 50)

    for epoch in range(epochs):
        train_metrics = train_epoch(model, train_loader, criterion, optimizer, device)
        val_metrics = evaluate(model, val_loader, criterion, device)

        scheduler.step(val_metrics["loss"])

        history["train_loss"].append(train_metrics["loss"])
        history["val_loss"].append(val_metrics["loss"])

        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch + 1}/{epochs} - Train Loss: {train_metrics['loss']:.4f} - Val Loss: {val_metrics['loss']:.4f}"
            )

        if val_metrics["loss"] < best_val_loss:
            best_val_loss = val_metrics["loss"]
            torch.save(model.state_dict(), save_path)
            print(f"  Saved best model (val_loss: {best_val_loss:.4f})")

    print("-" * 50)
    print(f"Training complete! Best model saved to {save_path}")

    return history


if __name__ == "__main__":
    print("Generating synthetic training data...")
    data = generate_synthetic_data(n_samples=2000)

    split = int(0.8 * len(data))
    train_data = data[:split]
    val_data = data[split:]

    print("Initializing feature extractor...")
    feature_extractor = FeatureExtractor()

    print(f"Feature dimension: {feature_extractor.feature_dim}")

    history = train_model(
        train_data=train_data,
        val_data=val_data,
        feature_extractor=feature_extractor,
        epochs=50,
        batch_size=32,
        save_path="D:/C-DAC/Helix-Zero6.0/cms_model/models/cms_model.pt",
    )

    print("\nTraining complete!")
    print(f"Final train loss: {history['train_loss'][-1]:.4f}")
    print(f"Final val loss: {history['val_loss'][-1]:.4f}")
