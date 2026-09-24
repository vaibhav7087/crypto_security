import os
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader

class PointDataset(Dataset):
    """For autoencoder: each sample is one feature vector."""
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
    
    def __len__(self):
        return len(self.X)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class SequenceDataset(Dataset):
    """For LSTM: each sample is a sliding window of `seq_len` consecutive feature vectors."""
    def __init__(self, X: np.ndarray, y: np.ndarray, seq_len: int = 10):
        self.seq_len = seq_len
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        
    def __len__(self):
        return len(self.X) - self.seq_len
        
    def __getitem__(self, idx):
        seq = self.X[idx : idx + self.seq_len]
        label = self.y[idx + self.seq_len]
        return seq, label

def get_dataloaders(config: dict) -> dict:
    """Returns a dict with point and sequence DataLoaders."""
    processed_dir = config['dataset']['processed_dir']
    
    # Load arrays
    X_train = np.load(os.path.join(processed_dir, 'X_train.npy'))
    y_train = np.load(os.path.join(processed_dir, 'y_train_binary.npy'))
    
    X_val = np.load(os.path.join(processed_dir, 'X_val.npy'))
    y_val = np.load(os.path.join(processed_dir, 'y_val_binary.npy'))
    
    X_test = np.load(os.path.join(processed_dir, 'X_test.npy'))
    y_test = np.load(os.path.join(processed_dir, 'y_test_binary.npy'))
    
    # Batch sizes
    ae_batch_size = config['autoencoder']['batch_size']
    lstm_batch_size = config['lstm']['batch_size']
    seq_len = config['lstm']['sequence_length']
    
    # Point datasets
    pt_train = PointDataset(X_train, y_train)
    pt_val = PointDataset(X_val, y_val)
    pt_test = PointDataset(X_test, y_test)
    
    # Sequence datasets
    seq_train = SequenceDataset(X_train, y_train, seq_len=seq_len)
    seq_val = SequenceDataset(X_val, y_val, seq_len=seq_len)
    seq_test = SequenceDataset(X_test, y_test, seq_len=seq_len)
    
    # Num workers = 0 on Windows is safer to avoid multiprocessing issues
    loaders = {
        'point_train': DataLoader(pt_train, batch_size=ae_batch_size, shuffle=True, num_workers=0),
        'point_val': DataLoader(pt_val, batch_size=ae_batch_size, shuffle=False, num_workers=0),
        'point_test': DataLoader(pt_test, batch_size=ae_batch_size, shuffle=False, num_workers=0),
        
        'seq_train': DataLoader(seq_train, batch_size=lstm_batch_size, shuffle=True, num_workers=0),
        'seq_val': DataLoader(seq_val, batch_size=lstm_batch_size, shuffle=False, num_workers=0),
        'seq_test': DataLoader(seq_test, batch_size=lstm_batch_size, shuffle=False, num_workers=0)
    }
    
    return loaders

def get_normal_only_loader(config):
    """Returns a DataLoader containing ONLY benign (label=0) samples for AE training."""
    processed_dir = config['dataset']['processed_dir']
    X_train = np.load(os.path.join(processed_dir, 'X_train.npy'))
    y_train = np.load(os.path.join(processed_dir, 'y_train_binary.npy'))
    
    normal_mask = y_train == 0
    X_normal = X_train[normal_mask]
    y_normal = y_train[normal_mask]
    
    dataset = PointDataset(X_normal, y_normal)
    return DataLoader(dataset, batch_size=config['autoencoder']['batch_size'], shuffle=True, num_workers=0)
