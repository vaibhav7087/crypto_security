import torch
import torch.nn as nn

class ThreatPredictor(nn.Module):
    """
    LSTM-based sequence model for threat prediction.
    Input: sequence of feature vectors (window of N time steps).
    Output: probability of attack in the next time step.
    """
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, dropout: float):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)
        )
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        lstm_out, (h_n, c_n) = self.lstm(x)
        # Use last hidden state for prediction
        last_hidden = lstm_out[:, -1, :]  # shape: (batch, hidden_dim)
        prediction = self.classifier(last_hidden)
        return prediction  # shape: (batch, 1) - probability of attack
