import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import time
import logging

logger = logging.getLogger(__name__)

class MetricsEngine:
    """
    Computes all required metrics for the research paper.
    """
    
    def __init__(self, config):
        self.config = config['evaluation']
        self.results = {}
        
    def evaluate_model(self, model_name: str, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None):
        """Calculate standard ML metrics."""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_true, y_pred, average='weighted', zero_division=0)
        }
        
        if y_prob is not None and len(np.unique(y_true)) == 2:
            try:
                metrics['auc_roc'] = roc_auc_score(y_true, y_prob)
            except ValueError:
                metrics['auc_roc'] = np.nan
                
        # False Positive Rate / False Negative Rate
        cm = confusion_matrix(y_true, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics['fpr'] = fp / (fp + tn) if (fp + tn) > 0 else 0
            metrics['fnr'] = fn / (fn + tp) if (fn + tp) > 0 else 0
            metrics['detection_rate'] = tp / (tp + fn) if (tp + fn) > 0 else 0
            
        if model_name not in self.results:
            self.results[model_name] = {}
        self.results[model_name].update(metrics)
        return metrics
        
    def log_latency(self, component: str, latency_ms: float):
        """Log latency for a specific component (e.g., 'pqc_handshake', 'inference')."""
        if 'latency' not in self.results:
            self.results['latency'] = {}
        if component not in self.results['latency']:
            self.results['latency'][component] = []
        self.results['latency'][component].append(latency_ms)
        
    def get_latency_stats(self, component: str):
        """Get mean/std/95th percentile latency."""
        if 'latency' not in self.results or component not in self.results['latency']:
            return None
        data = self.results['latency'][component]
        return {
            'mean_ms': np.mean(data),
            'std_ms': np.std(data),
            'p95_ms': np.percentile(data, 95)
        }
        
    def generate_report(self, output_path: str = "results/tables/metrics_report.csv"):
        """Export all metrics to a CSV report."""
        rows = []
        
        # ML Models
        for model, mets in self.results.items():
            if model == 'latency': continue
            row = {'Component': f"Model: {model}"}
            row.update(mets)
            rows.append(row)
            
        # Latency
        if 'latency' in self.results:
            for comp in self.results['latency'].keys():
                stats = self.get_latency_stats(comp)
                row = {
                    'Component': f"Latency: {comp}",
                    'mean_ms': stats['mean_ms'],
                    'std_ms': stats['std_ms'],
                    'p95_ms': stats['p95_ms']
                }
                rows.append(row)
                
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        logger.info(f"Metrics report saved to {output_path}")
        return df
