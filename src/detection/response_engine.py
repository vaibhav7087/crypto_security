import time
import logging

logger = logging.getLogger(__name__)

class AutonomousResponseEngine:
    """
    Takes anomaly scores from the detector and triggers proportional responses.
    """
    
    def __init__(self, config, blockchain_client=None, trust_manager=None, node_manager=None):
        self.thresholds = config['response']['severity_thresholds']
        self.cooldown = config['response']['action_cooldown_seconds']
        self.blockchain = blockchain_client
        self.trust_manager = trust_manager
        self.node_manager = node_manager
        self.action_log = []
        self.last_action_time = {}  # node_id -> last action timestamp
    
    def process_anomaly(self, node_id: str, anomaly_score: float, features: dict) -> dict:
        """
        Process an anomaly detection result and decide on response.
        """
        severity = self._classify_severity(anomaly_score)
        action = self._determine_action(severity)
        
        now = time.time()
        
        # Check cooldown
        if node_id in self.last_action_time:
            if now - self.last_action_time[node_id] < self.cooldown:
                return {'action': 'COOLDOWN', 'severity': severity, 'anomaly_score': float(anomaly_score)}
        
        # Execute action
        result = self._execute_action(action, node_id)
        self.last_action_time[node_id] = now
        
        # Log to blockchain
        ledger_tx_id = None
        if severity in ['HIGH', 'CRITICAL'] and self.blockchain:
            ledger_tx_id = self.blockchain.add_event({
                'type': 'ANOMALY_RESPONSE',
                'node_id': node_id,
                'anomaly_score': float(anomaly_score),
                'action': action,
                'timestamp': now
            })
        
        # Update trust score
        if self.trust_manager:
            self.trust_manager.penalize(node_id, float(anomaly_score))
        
        record = {
            'timestamp': now,
            'node_id': node_id,
            'anomaly_score': float(anomaly_score),
            'severity': severity,
            'action': action,
            'result': result,
            'ledger_tx_id': ledger_tx_id
        }
        self.action_log.append(record)
        return record
    
    def _classify_severity(self, score):
        if score < self.thresholds['low']:
            return 'NORMAL'
        elif score < self.thresholds['medium']:
            return 'LOW'
        elif score < self.thresholds['high']:
            return 'MEDIUM'
        elif score < self.thresholds['critical']:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _determine_action(self, severity):
        return {
            'NORMAL': 'NONE',
            'LOW': 'LOG_ONLY',
            'MEDIUM': 'THROTTLE_TRAFFIC',
            'HIGH': 'ISOLATE_CONTAINER',
            'CRITICAL': 'ISOLATE_AND_ALERT'
        }[severity]
    
    def _execute_action(self, action, node_id):
        """Execute the response action."""
        if action == 'NONE':
            return "No action required"
            
        logger.info(f"Executing action {action} on node {node_id}")
        
        if self.node_manager:
            try:
                if action == 'THROTTLE_TRAFFIC':
                    # In simulation, we'd limit container CPU/network
                    self.node_manager.throttle_node(node_id)
                    return "Throttled"
                elif action in ['ISOLATE_CONTAINER', 'ISOLATE_AND_ALERT']:
                    # Disconnect from network
                    self.node_manager.isolate_node(node_id)
                    return "Isolated"
            except Exception as e:
                logger.error(f"Failed to execute action on {node_id}: {e}")
                return f"Failed: {str(e)}"
                
        return "Simulated success (no node manager connected)"
