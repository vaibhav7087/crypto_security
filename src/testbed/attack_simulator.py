import time
import logging
import random
from src.testbed.workload_generator import WorkloadGenerator
from src.testbed.node_manager import NodeManager

logger = logging.getLogger(__name__)

class AttackSimulator:
    """
    Coordinates complex attack vectors on the testbed.
    """
    def __init__(self, config, node_manager: NodeManager, workload_gen: WorkloadGenerator):
        self.config = config['attacks']
        self.node_manager = node_manager
        self.workload_gen = workload_gen
        
    def simulate_distributed_ddos(self, duration: int):
        """Simulate a DDoS attack originating from multiple nodes targeting one."""
        nodes = list(self.node_manager.nodes.keys())
        if len(nodes) < 3:
            logger.error("Not enough nodes for distributed attack.")
            return
            
        target = nodes[0]
        attackers = nodes[1:3]
        
        logger.warning(f"Starting Distributed DDoS on {target} from {attackers}")
        
        for attacker in attackers:
            # We tell the attacker node to launch traffic at the target
            # In our simple mock, we just trigger the attack mode on the attacker to spike CPU
            self.node_manager.inject_attack(attacker, 'ddos_flood')
            
        time.sleep(duration)
        
        for attacker in attackers:
            self.workload_gen.stop_attack(attacker)
            
        logger.info("Distributed DDoS ended.")
        
    def simulate_data_exfiltration(self, target_node: str, duration: int):
        """Simulate an attacker exfiltrating data from a compromised node."""
        logger.warning(f"Starting Data Exfiltration on {target_node}")
        self.node_manager.inject_attack(target_node, 'data_exfiltration')
        time.sleep(duration)
        self.workload_gen.stop_attack(target_node)
        logger.info("Data Exfiltration ended.")
        
    def simulate_insider_threat(self, target_node: str, duration: int):
        """Simulate a compromised node altering transactions (triggers trust penalty)."""
        logger.warning(f"Starting Insider Threat on {target_node}")
        # In the full system, this would trigger the tamper_test logic
        self.node_manager.inject_attack(target_node, 'mitm')
        time.sleep(duration)
        self.workload_gen.stop_attack(target_node)
        logger.info("Insider Threat ended.")
