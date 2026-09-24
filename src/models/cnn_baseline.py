import torch
import torch.nn as nn

class CNN1DBaseline(nn.Module):
    """
    1D Convolutional Neural Network for intrusion detection.
    Processes sequences (time-series) to compare against our autoencoder+LSTM approach.
    """
    def __init__(self, input_dim: int, filters: list, kernel_size: int, dropout: float):
        super().__init__()
        
        # We will receive (batch, seq_len, input_dim)
        # Transpose to (batch, input_dim, seq_len)
        # So in_channels = input_dim
        self.conv_layers = nn.Sequential(
            nn.Conv1d(in_channels=input_dim, out_channels=filters[0], kernel_size=kernel_size, padding='same'),
            nn.BatchNorm1d(filters[0]),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            nn.Conv1d(in_channels=filters[0], out_channels=filters[1], kernel_size=kernel_size, padding='same'),
            nn.BatchNorm1d(filters[1]),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            nn.AdaptiveAvgPool1d(1)
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(filters[1], 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
            # No Sigmoid! Outputting logits for BCEWithLogitsLoss
        )
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        x = x.transpose(1, 2)  # shape: (batch, input_dim, seq_len)
        x = self.conv_layers(x) # shape: (batch, filters[1], 1)
        x = x.squeeze(-1) # shape: (batch, filters[1])
        return self.classifier(x) # shape: (batch, 1)
