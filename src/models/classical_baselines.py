import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

class IsolationForestBaseline:
    """Wrapper around sklearn Isolation Forest with same interface as our ANN."""
    def __init__(self, config):
        self.model = IsolationForest(
            n_estimators=config['n_estimators'],
            contamination=config['contamination'],
            random_state=config['random_state']
        )
    
    def fit(self, X_normal):
        """Train on normal data only."""
        self.model.fit(X_normal)
    
    def predict(self, X):
        """Returns: 1=normal, -1=anomaly (sklearn convention)."""
        return self.model.predict(X)
    
    def get_anomaly_score(self, X):
        """Returns anomaly scores (higher = more anomalous)."""
        # score_samples returns negative anomaly score
        return -self.model.score_samples(X)


class OneClassSVMBaseline:
    """Wrapper around sklearn One-Class SVM."""
    def __init__(self, config):
        self.model = OneClassSVM(
            kernel=config['kernel'],
            gamma=config['gamma'],
            nu=config['nu']
        )
        
    def fit(self, X_normal):
        """Train on normal data only."""
        self.model.fit(X_normal)
        
    def predict(self, X):
        """Returns: 1=normal, -1=anomaly."""
        return self.model.predict(X)
        
    def get_anomaly_score(self, X):
        """Higher = more anomalous."""
        return -self.model.score_samples(X)
