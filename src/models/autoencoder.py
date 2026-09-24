import torch
import torch.nn as nn
import numpy as np

class AnomalyAutoencoder(nn.Module):
    """
    Symmetric autoencoder for anomaly detection.
    Trained ONLY on normal traffic.
    Anomaly = reconstruction error > threshold.
    """
    def __init__(self, input_dim: int, hidden_dims: list, latent_dim: int, dropout: float = 0.2):
        super().__init__()
        
        # Encoder: input_dim -> hidden_dims -> latent_dim
        encoder_layers = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, h_dim),
                nn.BatchNorm1d(h_dim),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_dim = h_dim
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder: latent_dim -> reversed(hidden_dims) -> input_dim
        decoder_layers = []
        prev_dim = latent_dim
        for h_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, h_dim),
                nn.BatchNorm1d(h_dim),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_dim = h_dim
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        # Use Sigmoid if input is MinMax scaled [0, 1]
        decoder_layers.append(nn.Sigmoid())
        self.decoder = nn.Sequential(*decoder_layers)
    
    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent
    
    def get_anomaly_score(self, x):
        """MSE reconstruction error per sample."""
        self.eval()
        with torch.no_grad():
            reconstructed, _ = self.forward(x)
            mse = torch.mean((x - reconstructed) ** 2, dim=1)
        return mse
    
    def get_threshold(self, normal_data_loader, percentile=95):
        """Compute anomaly threshold from normal data reconstruction errors."""
        self.eval()
        errors = []
        device = next(self.parameters()).device
        with torch.no_grad():
            for batch, _ in normal_data_loader:
                batch = batch.to(device)
                reconstructed, _ = self.forward(batch)
                mse = torch.mean((batch - reconstructed) ** 2, dim=1)
                errors.extend(mse.cpu().numpy())
        return np.percentile(errors, percentile)
