import time
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import logging
from sklearn.model_selection import KFold
from torch.utils.data import DataLoader, Subset
from src.preprocessing.data_loader import PointDataset, SequenceDataset

logger = logging.getLogger(__name__)

def train_model(model, train_loader, val_loader, config, model_type="autoencoder"):
    """
    Train a model with early stopping.
    """
    device = config.get('device', 'cpu')
    model.to(device)
    
    # Configure optimizer and loss
    lr = config.get('learning_rate', 0.001)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    if model_type == "autoencoder":
        criterion = nn.MSELoss()
    else: # lstm or cnn
        # We will compute pos_weight dynamically per batch or just use a generic one
        # but BCEWithLogitsLoss needs pos_weight as a tensor
        pass # Created dynamically below
        
    epochs = config.get('epochs', 50)
    patience = config.get('early_stopping_patience', 5)
    
    train_losses = []
    val_losses = []
    
    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None
    
    start_time = time.time()
    
    for epoch in range(epochs):
        model.train()
        epoch_train_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device).float()
            
            optimizer.zero_grad()
            
            if model_type == "autoencoder":
                reconstructed, _ = model(X_batch)
                loss = criterion(reconstructed, X_batch)
            else:
                preds = model(X_batch).squeeze()
                # Compute class imbalance weight for this batch
                num_pos = torch.sum(y_batch)
                num_neg = len(y_batch) - num_pos
                # If no positives, default to 1.0 to avoid division by zero
                pos_weight = (num_neg / num_pos) if num_pos > 0 else torch.tensor(1.0).to(device)
                
                criterion_cls = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
                loss = criterion_cls(preds, y_batch)
                
            loss.backward()
            optimizer.step()
            
            epoch_train_loss += loss.item() * X_batch.size(0)
            
        epoch_train_loss /= len(train_loader.dataset)
        train_losses.append(epoch_train_loss)
        
        # Validation
        model.eval()
        epoch_val_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device).float()
                
                if model_type == "autoencoder":
                    reconstructed, _ = model(X_batch)
                    loss = criterion(reconstructed, X_batch)
                else:
                    preds = model(X_batch).squeeze()
                    num_pos = torch.sum(y_batch)
                    num_neg = len(y_batch) - num_pos
                    pos_weight = (num_neg / num_pos) if num_pos > 0 else torch.tensor(1.0).to(device)
                    criterion_cls = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
                    loss = criterion_cls(preds, y_batch)
                    
                epoch_val_loss += loss.item() * X_batch.size(0)
                
        epoch_val_loss /= len(val_loader.dataset)
        val_losses.append(epoch_val_loss)
        
        logger.debug(f"Epoch {epoch+1}/{epochs} - Train Loss: {epoch_train_loss:.4f} - Val Loss: {epoch_val_loss:.4f}")
        
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break
                
    training_time = time.time() - start_time
    
    # Restore best model
    if best_model_state:
        model.load_state_dict(best_model_state)
        
    return {
        'model': model,
        'train_losses': train_losses,
        'val_losses': val_losses,
        'best_epoch': epoch - patience_counter,
        'training_time': training_time
    }

def save_model(model, path, metadata=None):
    """Save model state dict + metadata."""
    torch.save({
        'model_state_dict': model.state_dict(),
        'metadata': metadata
    }, path)
