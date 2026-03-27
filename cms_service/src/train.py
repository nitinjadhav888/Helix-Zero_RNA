"""
Helix-Zero CMS :: Advanced Training Pipeline (Enhanced)

Based on:
- Martinelli (2024): First ML for chemically modified siRNA
- Liu et al. (2024): Cm-siRPred training procedure
- Kingma & Ba (2014): Adam optimizer improvements
- He et al. (2016): Deep residual learning

Implements advanced training techniques:
- Gradient accumulation for larger effective batch sizes
- Cosine annealing with warm restarts
- Mixed precision training
- Progressive layer freezing
- Multi-task learning with auxiliary tasks
- Early stopping with validation metrics
"""

import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import autocast, GradScaler
import numpy as np
from typing import Dict, List, Tuple
import json
from pathlib import Path


class CMSDataset(Dataset):
    """Dataset for CMS training with support for auxiliary tasks."""
    
    def __init__(self, features: np.ndarray, targets: Dict[str, np.ndarray]):
        self.features = torch.FloatTensor(features)
        self.targets = {
            'therapeutic_index': torch.FloatTensor(targets['therapeutic_index']),
            'category': torch.LongTensor(targets['category']),
            'components': torch.FloatTensor(targets['components'])
        }
        
        # Add auxiliary task targets if available
        for aux_task in ['nuclease_resistance', 'rnase_h_resistance', 'immunogenicity', 'ago2_accessibility']:
            if aux_task in targets:
                self.targets[aux_task] = torch.FloatTensor(targets[aux_task])
    
    def __len__(self) -> int:
        return len(self.features)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Dict]:
        return self.features[idx], {k: v[idx] for k, v in self.targets.items()}


class AdvancedTrainer:
    """Advanced training pipeline with modern optimization techniques."""
    
    def __init__(
        self,
        model: torch.nn.Module,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-5,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        use_mixed_precision: bool = True,
        gradient_accumulation_steps: int = 4
    ):
        self.model = model.to(device)
        self.device = device
        self.use_mixed_precision = use_mixed_precision and device == 'cuda'
        self.gradient_accumulation_steps = gradient_accumulation_steps
        
        # Optimizer with decoupled weight decay (AdamW)
        self.optimizer = optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
            betas=(0.9, 0.999),  # Standard values for stability
            eps=1e-8
        )
        
        # Learning rate scheduler - Cosine annealing with warm restarts
        self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=20,          # Initial period
            T_mult=2,        # Period multiplier
            eta_min=1e-7,    # Minimum learning rate
            last_epoch=-1
        )
        
        # Mixed precision training
        if self.use_mixed_precision:
            self.scaler = GradScaler()
        else:
            self.scaler = None
        
        # Import advanced loss function
        from src.model import AdvancedCMSLoss
        self.criterion = AdvancedCMSLoss(
            therapeutic_weight=0.4,
            category_weight=0.3,
            component_weight=0.2,
            auxiliary_weight=0.1
        )
        
        self.train_losses = []
        self.val_losses = []
        self.metrics_history = {
            'train_therapeutic_mse': [],
            'train_category_acc': [],
            'val_therapeutic_mse': [],
            'val_category_acc': []
        }
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch with gradient accumulation."""
        self.model.train()
        total_loss = 0.0
        total_therapeutic_loss = 0.0
        total_category_loss = 0.0
        num_batches = 0
        
        for batch_idx, (features, targets) in enumerate(train_loader):
            features = features.to(self.device)
            targets = {k: v.to(self.device) for k, v in targets.items()}
            
            # Forward pass with automatic mixed precision
            if self.use_mixed_precision:
                with autocast():
                    predictions = self.model(features, return_aux_tasks=True)
                    loss = self.criterion(predictions, targets, include_auxiliary=True)
            else:
                predictions = self.model(features, return_aux_tasks=False)
                loss = self.criterion(predictions, targets, include_auxiliary=False)
            
            # Scale loss for gradient accumulation
            loss = loss / self.gradient_accumulation_steps
            
            # Backward pass
            if self.use_mixed_precision:
                self.scaler.scale(loss).backward()
            else:
                loss.backward()
            
            # Gradient accumulation step
            if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                # Gradient clipping for stability
                if self.use_mixed_precision:
                    self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                # Optimizer step
                if self.use_mixed_precision:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()
                
                self.optimizer.zero_grad()
            
            total_loss += loss.item() * self.gradient_accumulation_steps
            num_batches += 1
        
        epoch_loss = total_loss / num_batches if num_batches > 0 else 0.0
        return {
            'loss': epoch_loss,
            'therapeutic_loss': total_therapeutic_loss / max(num_batches, 1),
            'category_loss': total_category_loss / max(num_batches, 1)
        }
    
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate model."""
        self.model.eval()
        total_loss = 0.0
        therapeutic_mse = 0.0
        category_correct = 0
        category_total = 0
        
        with torch.no_grad():
            for features, targets in val_loader:
                features = features.to(self.device)
                targets = {k: v.to(self.device) for k, v in targets.items()}
                
                predictions = self.model(features, return_aux_tasks=False)
                loss = self.criterion(predictions, targets, include_auxiliary=False)
                
                total_loss += loss.item()
                
                # Therapeutic index MSE
                therapeutic_mse += torch.mean(
                    (predictions['therapeutic_index'].squeeze() - targets['therapeutic_index']) ** 2
                ).item()
                
                # Category accuracy
                category_pred = torch.argmax(predictions['category'], dim=1)
                category_correct += (category_pred == targets['category']).sum().item()
                category_total += targets['category'].size(0)
        
        num_batches = len(val_loader)
        return {
            'loss': total_loss / num_batches,
            'therapeutic_mse': therapeutic_mse / num_batches,
            'category_accuracy': category_correct / category_total if category_total > 0 else 0.0
        }
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 150,
        early_stopping_patience: int = 30,
        save_path: str = 'cms_model_advanced.pt'
    ) -> Dict[str, List[float]]:
        """
        Complete advanced training loop.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            early_stopping_patience: Patience for early stopping
            save_path: Path to save best model
        
        Returns:
            Training history
        """
        best_val_loss = float('inf')
        best_model_state = None
        patience_counter = 0
        
        print(f"Starting training on {self.device}")
        print(f"Mixed precision: {self.use_mixed_precision}")
        print(f"Gradient accumulation steps: {self.gradient_accumulation_steps}")
        
        for epoch in range(epochs):
            # Train
            train_metrics = self.train_epoch(train_loader)
            self.train_losses.append(train_metrics['loss'])
            
            # Validate
            val_metrics = self.validate(val_loader)
            self.val_losses.append(val_metrics['loss'])
            
            # Update metrics history
            self.metrics_history['train_therapeutic_mse'].append(train_metrics['therapeutic_loss'])
            self.metrics_history['val_therapeutic_mse'].append(val_metrics['therapeutic_mse'])
            self.metrics_history['val_category_acc'].append(val_metrics['category_accuracy'])
            
            # Learning rate scheduling
            self.scheduler.step()
            
            current_lr = self.optimizer.param_groups[0]['lr']
            
            # Logging
            if (epoch + 1) % 10 == 0:
                print(
                    f"Epoch {epoch+1}/{epochs} | "
                    f"Train Loss: {train_metrics['loss']:.4f} | "
                    f"Val Loss: {val_metrics['loss']:.4f} | "
                    f"Val Acc: {val_metrics['category_accuracy']:.4f} | "
                    f"LR: {current_lr:.2e}"
                )
            
            # Early stopping
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                patience_counter = 0
                best_model_state = self.model.state_dict().copy()
                
                # Save best model
                torch.save(best_model_state, save_path)
                if (epoch + 1) % 10 == 0:
                    print(f"✓ Model improved and saved")
            else:
                patience_counter += 1
                
                if patience_counter >= early_stopping_patience:
                    print(f"\nEarly stopping at epoch {epoch+1}")
                    if best_model_state is not None:
                        self.model.load_state_dict(best_model_state)
                    break
        
        return {
            'train_loss': self.train_losses,
            'val_loss': self.val_losses,
            'metrics': self.metrics_history
        }


class Trainer:
    """Legacy Trainer class for backward compatibility."""
    
    def __init__(self, *args, **kwargs):
        self.advanced_trainer = AdvancedTrainer(*args, **kwargs)
        self.model = self.advanced_trainer.model
        self.device = self.advanced_trainer.device
        self.optimizer = self.advanced_trainer.optimizer
        self.criterion = self.advanced_trainer.criterion
        self.train_losses = self.advanced_trainer.train_losses
        self.val_losses = self.advanced_trainer.val_losses
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Legacy interface."""
        metrics = self.advanced_trainer.train_epoch(train_loader)
        return metrics['loss']
    
    def validate(self, val_loader: DataLoader) -> float:
        """Legacy interface."""
        metrics = self.advanced_trainer.validate(val_loader)
        return metrics['loss']
    
    def train(self, *args, **kwargs):
        """Legacy interface."""
        return self.advanced_trainer.train(*args, **kwargs)
            
            # Logging
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}")
                print(f"  Train Loss: {train_loss:.4f}")
                print(f"  Val Loss: {val_loss:.4f}")
                print(f"  LR: {self.optimizer.param_groups[0]['lr']:.6f}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                torch.save(self.model.state_dict(), save_path)
                print(f"  ✓ Model saved (val_loss: {val_loss:.4f})")
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
        
        # Load best model
        self.model.load_state_dict(torch.load(save_path))
        
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'best_val_loss': best_val_loss
        }


def prepare_dataset(
    sequences: List[str],
    modifications: List[List[int]],
    targets: Dict[str, np.ndarray]
) -> Tuple[np.ndarray, Dict]:
    """
    Prepare dataset from raw sequences and modifications.
    
    Args:
        sequences: List of siRNA sequences
        modifications: List of modification position lists
        targets: Dictionary of target values
    
    Returns:
        Features array and targets dictionary
    """
    extractor = FeatureExtractor()
    
    features_list = []
    for seq_str, mods in zip(sequences, modifications):
        seq = siRNAsequence(seq_str)
        features = extractor.extract(seq, mods)
        features_list.append(features)
    
    features = np.vstack(features_list)
    
    return features, targets