import time
import pandas as pd
import numpy as np
from collections import deque
import logging
from sklearn.metrics import f1_score
import torch
from torch.utils.data import DataLoader
from src.preprocessing.data_loader import PointDataset

logger = logging.getLogger(__name__)

class AdaptiveRetrainer:
    """
    Manages the sliding-window retraining cycle for the Autoencoder.
    """
    
    def __init__(self, model, config, threshold):
        self.model = model
        self.config = config['adaptive']
        self.threshold = threshold
        self.buffer = deque(maxlen=self.config['window_size'])
        self.retrain_interval = self.config['retrain_interval']
        self.drift_threshold = self.config['drift_detection_threshold']
        self.retrain_log = []
        self.samples_since_retrain = 0
        self.current_f1 = None
        self._last_convergence_epochs = 0
        self.device = next(model.parameters()).device
    
    def add_samples(self, X_new, y_new):
        """Add new samples to the buffer."""
        for x, y in zip(X_new, y_new):
            self.buffer.append((x, y))
        self.samples_since_retrain += len(X_new)
        
        if self.samples_since_retrain >= self.retrain_interval:
            if len(self.buffer) >= self.config['min_samples_for_retrain']:
                return self._check_and_retrain()
        return False
    
    def _check_and_retrain(self):
        """Check if drift occurred, retrain if needed."""
        X_buf = np.array([s[0] for s in self.buffer])
        y_buf = np.array([s[1] for s in self.buffer])
        
        new_f1 = self._evaluate(X_buf, y_buf)
        
        drift_detected = False
        if self.current_f1 is not None:
            f1_drop = self.current_f1 - new_f1
            if f1_drop > self.drift_threshold:
                drift_detected = True
                logger.info(f"Concept drift detected! F1 dropped by {f1_drop:.4f}")
        
        # Only retrain if drift detected or first time
        if drift_detected or self.current_f1 is None:
            start_time = time.time()
            X_normal = X_buf[y_buf == 0]
            if len(X_normal) > 0:
                self._retrain(X_normal)
            else:
                logger.warning("No normal samples in buffer for retraining.")
            retrain_duration = time.time() - start_time
        else:
            retrain_duration = 0.0
        
        post_retrain_f1 = self._evaluate(X_buf, y_buf)
        
        self.retrain_log.append({
            'timestamp': time.time(),
            'drift_detected': drift_detected,
            'pre_retrain_f1': new_f1,
            'post_retrain_f1': post_retrain_f1,
            'retrain_duration_seconds': retrain_duration,
            'buffer_size': len(self.buffer),
            'convergence_epochs': self._last_convergence_epochs
        })
        
        self.current_f1 = post_retrain_f1
        self.samples_since_retrain = 0
        return True
    
    def _retrain(self, X_normal):
        """Quick incremental retrain on new normal data."""
        dataset = PointDataset(X_normal, np.zeros(len(X_normal))) # labels don't matter for AE
        # Use a small batch size for the small window
        loader = DataLoader(dataset, batch_size=64, shuffle=True)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-4) # lower LR for fine-tuning
        criterion = torch.nn.MSELoss()
        
        self.model.train()
        epochs = self.config['max_retrain_epochs']
        for epoch in range(epochs):
            epoch_loss = 0
            for batch_x, _ in loader:
                batch_x = batch_x.to(self.device)
                optimizer.zero_grad()
                reconstructed, _ = self.model(batch_x)
                loss = criterion(reconstructed, batch_x)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
        
        self._last_convergence_epochs = epochs
        
        # Update threshold after retraining
        self.threshold = self.model.get_threshold(loader)
    
    def _evaluate(self, X, y):
        """Evaluate model F1 on given data."""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            scores = self.model.get_anomaly_score(X_tensor).cpu().numpy()
            
        preds = (scores > self.threshold).astype(int)
        return f1_score(y, preds, zero_division=0)
    
    def get_retrain_log(self):
        """Return the log as a DataFrame for analysis."""
        return pd.DataFrame(self.retrain_log)
