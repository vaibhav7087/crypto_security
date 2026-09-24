import time
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class TrustManager:
    """
    Dynamic trust scoring for each node in the network.
    """
    
    def __init__(self, config, blockchain):
        self.config = config['trust']
        self.blockchain = blockchain
        self.trust_scores = {}    # node_id -> float
        self.trust_history = {}   # node_id -> list of (timestamp, score, reason)
        
    def register_node(self, node_id: str):
        """Initialize a node with default trust score."""
        self.trust_scores[node_id] = self.config['initial_score']
        self.trust_history[node_id] = [(time.time(), self.config['initial_score'], 'INIT')]
        
    def penalize(self, node_id: str, anomaly_score: float, threshold: float = 0.000784):
        """Reduce trust based on anomaly severity relative to decision threshold."""
        if anomaly_score > 0 and threshold > 0:
            # Scale penalty so zero-day threats incur visible, proportional penalties
            severity_ratio = min(max(anomaly_score / threshold, 1.0), 3.0)
            penalty = 0.028 * severity_ratio  # ~0.07 penalty: Round 1 Throttled (0.43), Round 2 Quarantined (<0.40)
        else:
            penalty = self.config['anomaly_penalty'] * anomaly_score
        self._update_score(node_id, -penalty, f'ANOMALY_{anomaly_score:.3f}')
        
    def reward_signature(self, node_id: str):
        """Increase trust for valid cryptographic signature."""
        self._update_score(node_id, self.config['valid_signature_reward'], 'VALID_SIG')
        
    def reward_uptime(self, node_id: str, minutes: float):
        """Increase trust based on uptime."""
        reward = self.config['uptime_reward_per_minute'] * minutes
        self._update_score(node_id, reward, f'UPTIME_{minutes:.0f}min')
        
    def recover(self, node_id: str):
        """Gradual trust recovery after clean behavior."""
        self._update_score(node_id, self.config['recovery_rate'], 'RECOVERY')
        
    def is_trusted(self, node_id: str) -> bool:
        """Check if node is above isolation threshold."""
        return self.trust_scores.get(node_id, 0) >= self.config['isolation_threshold']
        
    def _update_score(self, node_id, delta, reason):
        """Clamp score to [min, max], record history, log to blockchain."""
        if node_id not in self.trust_scores:
            self.register_node(node_id)
            
        old_score = self.trust_scores[node_id]
        new_score = max(self.config['min_score'], 
                       min(self.config['max_score'], old_score + delta))
                       
        self.trust_scores[node_id] = new_score
        self.trust_history[node_id].append((time.time(), new_score, reason))
        
        # Log to blockchain
        if self.blockchain:
            self.blockchain.add_event({
                'type': 'TRUST_UPDATE',
                'node_id': node_id,
                'old_score': old_score,
                'new_score': new_score,
                'delta': delta,
                'reason': reason
            })
            
    def get_trust_trajectory(self, node_id: str) -> pd.DataFrame:
        """Return trust history as DataFrame for plotting."""
        if node_id not in self.trust_history:
            return pd.DataFrame()
        return pd.DataFrame(self.trust_history[node_id], columns=['timestamp', 'score', 'reason'])
